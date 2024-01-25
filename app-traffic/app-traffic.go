package main

import (
	"flag"
	"log"

	"github.com/deepflowio/deepflow-auto-test/app-traffic/client"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/client/redis"
	"go.uber.org/ratelimit"
)

var (
	fhost    = flag.String("h", "localhost:12345", "Target host:port")
	fpasswd  = flag.String("p", "", "DB password")
	frate    = flag.Int("r", 100000, "Packets per second")
	fthreads = flag.Int("t", 1, "Number of threads")
	fengine  = flag.String("e", "", "Engine of DB [redis, mysql]")
)

func main() {
	flag.Parse()
	var engineClinet client.EngineClient
	if *fengine == "redis" {
		engineClinet = &redis.RedisClient{
			Addr:     *fhost,
			Password: *fpasswd,
			DB:       0,
		}
		engineClinet.InitClient()
	} else if *fengine == "mysql" {

	} else {
		log.Fatal("fengine, -e, should be designed [redis, mysql]")
	}
	defer engineClinet.Close()

	for i := 0; i < *fthreads; i++ {
		go func(index int) {
			rate := (*frate + *fthreads - 1) / *fthreads
			log.Printf("[*] Start %s App Traffic %s, date rate %d pps.\n", *fengine, *fhost, rate)

			// flood
			// Take 10 tokens each time to avoid too high call frequency of the Take() function
			rate_limit := ratelimit.New(rate / 10)
			for {
				rate_limit.Take()
				engineClinet.Exec()
				engineClinet.Exec()
				engineClinet.Exec()
				engineClinet.Exec()
				engineClinet.Exec()
				engineClinet.Exec()
				engineClinet.Exec()
				engineClinet.Exec()
				engineClinet.Exec()
				engineClinet.Exec()
			}
		}(i)
	}

	// Forever
	<-make(chan bool, 1)
}
