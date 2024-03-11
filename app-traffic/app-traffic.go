package main

import (
	"flag"
	"fmt"
	"log"
	"time"

	"github.com/deepflowio/deepflow-auto-test/app-traffic/client"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/grpc"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/mongo"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/mysql"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/redis"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
	"go.uber.org/ratelimit"
)

var (
	fhost       = flag.String("h", "", "Target host:port")
	fpasswd     = flag.String("p", "", "DB password")
	frate       = flag.Int("r", 0, "Packets per second")
	fthreads    = flag.Int("t", 1, "Number of threads")
	fengine     = flag.String("e", "", "Engine of protocol [redis, mysql, mongo, grpc]")
	fduration   = flag.Int("d", 0, "execution time in seconds")
	fconcurrent = flag.Int("c", 1, "concurrent connections of each thread")
	fcomplexity = flag.Int("complexity", 1, "complexity of query sql")
	fmethod     = flag.String("method", "", "method of query, redis:[GET, SET]")
	fsql        = flag.String("sql", "", "customizable sql of query, only support mysql")
	fdb         = flag.String("db", "", "db of mysql or redis")
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
	if *fengine == "" || (*fengine != "mysql" && *fengine != "redis" && *fengine != "grpc" && *fengine != "mongo") {
		log.Fatal("fengine -e should be assigned [redis, mysql, grpc, mongo]")
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
	var count int
	var err int
	var rateTokenCount int

	rps_rate := (*frate + *fthreads - 1) / *fthreads

	rate := rps_rate / *fconcurrent
	startChan := make(chan int, *fthreads)
	var startTime time.Time
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
				Addr:       *fhost,
				Password:   *fpasswd,
				DB:         0,
				Complexity: *fcomplexity,
				Method:     *fmethod,
			}
		} else if *fengine == "mysql" {
			engineClinet = &mysql.MysqlClient{
				Addr:         *fhost,
				Password:     *fpasswd,
				DB:           *fdb,
				User:         "root",
				SessionCount: *fconcurrent,
				Complexity:   *fcomplexity,
				Sql:          *fsql,
			}
		} else if *fengine == "grpc" {
			engineClinet = &grpc.GrpcClient{
				Addr: *fhost,
			}
		} else if *fengine == "mongo" {
			engineClinet = &mongo.MongoClient{
				Addr:       *fhost,
				Password:   *fpasswd,
				DB:         *fdb,
				Complexity: *fcomplexity,
			}
		}
		engines[i] = engineClinet

		// Take 10 tokens each time to avoid too high call frequency of the Take() function
		// WithoutSlack cancel maxSlack

		go func(index int) {
			engineClinet.InitClient()
			defer engineClinet.Close()
			log.Printf("[*] Start %s App Traffic %s, date rate %d rps.\n", *fengine, *fhost, rps_rate)
			rate_limit := ratelimit.New(rateTokenCount, ratelimit.WithoutSlack)
			execCount := rate / rateTokenCount
			// wait all thread ready
			<-startChan
			for {
				rate_limit.Take()
				for i := 0; i < execCount; i++ {
					engineClinet.Exec()
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
	startTime = time.Now()
	// start all clinet
	for i := 0; i < *fthreads; i++ {
		startChan <- 1
	}

	times := 0
	for {
		time.Sleep(time.Duration(1) * time.Second)
		count = 0
		err = 0
		for i := 0; i < *fthreads; i++ {
			count += engines[i].GetCount()
			err += engines[i].GetErrCount()
		}
		fmt.Printf("now request count is %d , err is %d, cost time %.6fs\n", count, err, time.Since(startTime).Seconds())
		times += 1
		if *fthreads > 0 && times >= *fduration {
			break
		}
	}
	// Calculate total duration
	lantencyResult := &common.LantencyResult{
		ExecSeconds: time.Since(startTime).Seconds(),
	}
	for i := 0; i < *fthreads; i++ {
		lantencyResult.Append(engines[i].GetLantency())
	}
	// Print result
	lantencyResult.Print()

	// Forever
	// <-make(chan bool, 1)
}
