package main

import (
	"flag"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/deepflowio/deepflow-auto-test/app-traffic/client"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/grpc"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/http"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/mongo"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/mysql"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/redis"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
	"go.uber.org/ratelimit"
)

var SUPPORT_ENGINES = []string{"redis", "mysql", "mongo", "grpc", "h2c", "https", "http"}

var (
	fhost       = flag.String("h", "", "Target host:port")
	fpasswd     = flag.String("p", "", "DB password")
	frate       = flag.Int("r", 0, "Packets per second")
	fthreads    = flag.Int("t", 1, "Number of threads")
	fengine     = flag.String("e", "", fmt.Sprintf("Engine of protocol %v", SUPPORT_ENGINES))
	fduration   = flag.Int("d", 0, "execution time in seconds")
	fconcurrent = flag.Int("c", 1, "concurrent connections of each thread")

	fcomplexity = flag.Int("complexity", 1, "complexity of query sql")
	fmethod     = flag.String("method", "", "method of query, redis:[GET, SET], http2:[GET, POST]")
	fsql        = flag.String("sql", "", "customizable sql of query, only support mysql")
	fdb         = flag.String("db", "", "database name, support [redis, mysql, mongo]")
	fdataSize   = flag.Int("datasize", 1, "body size of http/http2 query")
	fkeepalive  = flag.Bool("keepalive", true, "keepalive of each http client")
)

func main() {
	flag.Parse()

	// check flag
	if *fhost == "" {
		log.Fatal("fhost -h should be assigned")
	}
	if *frate == 0 {
		log.Fatal("frate -r should be assigned")
	}
	if *fengine == "" || !strings.Contains(strings.Join(SUPPORT_ENGINES, " "), *fengine) {
		log.Fatal(fmt.Sprintf("fengine -e should be assigned %v", SUPPORT_ENGINES))
	}
	if *fduration == 0 {
		log.Fatal("fduration -d should be assigned")
	}
	if *fconcurrent > 1 && (*fthreads)*(*fconcurrent)*10 > *frate {
		log.Fatal("(fthreads * fconcurrent * 10) should be less than (frate)")
	}
	if *fcomplexity < 1 {
		log.Fatal("fcomplexity should > 0")
	}

	engines := make([]client.EngineClient, *fthreads)
	var rateTokenCount int // exec count of each token

	rps_rate := (*frate + *fthreads - 1) / *fthreads
	rate := rps_rate / *fconcurrent

	startChan := make(chan int, *fthreads) // use to start all thread
	stopChan := make(chan int, *fthreads)
	endChan := make(chan int, 1)
	var startTime time.Time

	latencyChan := make(chan *time.Duration, 10000)
	errLatencyChan := make(chan *time.Duration, 10000)

	latencyResult := &common.LatencyResult{}
	latencyResult.Init()
	// token count per second
	// token count = rps_rate / concurrent count of each client / exec count of each token(10 or 5 or 1)
	if rate%10 == 0 {
		rateTokenCount = rate / 10
	} else if rate%5 == 0 {
		rateTokenCount = rate / 5
	} else {
		rateTokenCount = rate
	}

	for i := 0; i < *fthreads; i++ {
		var engineClinet client.EngineClient
		if *fengine == "redis" {
			engineClinet = &redis.RedisClient{
				LatencyChan:    latencyChan,
				ErrLatencyChan: errLatencyChan,
				Addr:           *fhost,
				Password:       *fpasswd,
				DB:             0,
				Complexity:     *fcomplexity,
				Method:         *fmethod,
			}
		} else if *fengine == "mysql" {
			engineClinet = &mysql.MysqlClient{
				LatencyChan:    latencyChan,
				ErrLatencyChan: errLatencyChan,
				Addr:           *fhost,
				Password:       *fpasswd,
				DB:             *fdb,
				User:           "root",
				SessionCount:   *fconcurrent,
				Complexity:     *fcomplexity,
				Sql:            *fsql,
			}
		} else if *fengine == "grpc" {
			engineClinet = &grpc.GrpcClient{
				LatencyChan:    latencyChan,
				ErrLatencyChan: errLatencyChan,
				Addr:           *fhost,
			}
		} else if *fengine == "mongo" {
			engineClinet = &mongo.MongoClient{
				LatencyChan:    latencyChan,
				ErrLatencyChan: errLatencyChan,
				Addr:           *fhost,
				Password:       *fpasswd,
				DB:             *fdb,
				Complexity:     *fcomplexity,
			}
		} else if *fengine == "h2c" {
			engineClinet = &http.HttpClient{
				LatencyChan:    latencyChan,
				ErrLatencyChan: errLatencyChan,
				Addr:           *fhost,
				Method:         *fmethod,
				Complexity:     *fcomplexity,
				DataSize:       *fdataSize,
				KeepAlive:      *fkeepalive,
				H2C:            true,
				TLS:            false,
			}
		} else if *fengine == "https" {
			engineClinet = &http.HttpClient{
				LatencyChan:    latencyChan,
				ErrLatencyChan: errLatencyChan,
				Addr:           *fhost,
				Method:         *fmethod,
				Complexity:     *fcomplexity,
				DataSize:       *fdataSize,
				KeepAlive:      *fkeepalive,
				H2C:            false,
				TLS:            true,
			}
		}

		engines[i] = engineClinet
		if i == 0 {
			engineClinet.Property()
		}

		// Take 10 tokens each time to avoid too high call frequency of the Take() function
		// WithoutSlack cancel maxSlack

		go func(index int) {
			engineClinet.InitClient()
			defer engineClinet.Close()
			log.Printf("[*] Start %s App Traffic %s, date rate %d rps.\n", *fengine, *fhost, rps_rate)
			rate_limit := ratelimit.New(rateTokenCount, ratelimit.WithoutSlack)
			// exec count of each token
			execCount := rate / rateTokenCount
			// wait all thread ready
			<-startChan
			for {
				select {
				case <-stopChan:
					return
				default:
					rate_limit.Take()
					for j := 0; j < execCount; j++ {
						engineClinet.Exec()
					}
				}
			}
		}(i)
	}

	// wait all client ready
	for {
		ready := true
		for i := 0; i < *fthreads; i++ {
			if !engines[i].IsReady() {
				ready = false
			}
		}
		if ready {
			break
		}
		time.Sleep(time.Duration(100) * time.Millisecond)
	}

	// accept latencyfrom exec thread
	go func() {
		var lt *time.Duration
		var elt *time.Duration
		for {
			select {
			case <-endChan:
				return
			case lt = <-latencyChan: // latencyfrom success exec
				latencyResult.Append(lt, false)
			case elt = <-errLatencyChan: // latencyfrom error exec
				latencyResult.Append(elt, true)
			default:
				time.Sleep(time.Duration(10) * time.Millisecond)
				continue
			}
		}
	}()
	times := 0
	// start all clinet
	startTime = time.Now()
	for i := 0; i < *fthreads; i++ {
		startChan <- 1
	}
	for {
		time.Sleep(time.Duration(1) * time.Second)
		fmt.Printf("now request count about %d , errCount about %d, cost time %.6fs\n", latencyResult.Count, latencyResult.ErrCount, time.Since(startTime).Seconds())
		times += 1
		if *fthreads > 0 && times >= *fduration {
			for i := 0; i < *fthreads; i++ {
				stopChan <- 1
			}
			endChan <- 1
			latencyResult.ExecSeconds = time.Since(startTime).Seconds()
			break
		}
	}
	// Print result
	latencyResult.Print()

}
