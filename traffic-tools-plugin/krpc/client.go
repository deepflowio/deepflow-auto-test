package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

const (
	REQUEST_INTERVAL = time.Second / 10
)

var (
	requestPerSecond = flag.Int("r", 100, "request per second")
	clusterIP        = flag.String("h", "", "krpc pod clusterIP")
)

func newRequest(client *http.Client, req *http.Request) {

	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("request err:", err)
		return
	}
	defer resp.Body.Close()
	_, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("read response err", err)
		return
	}

	time.Sleep(REQUEST_INTERVAL)
}

func main() {
	flag.Parse()
	sleepCounter := 0
	timeStart := time.Now()
	transport := &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 100,
	}
	client := &http.Client{
		Transport: transport,
		Timeout:   100 * time.Second,
	}
	req, err := http.NewRequest("GET", "http://"+*clusterIP+":8450/v1/openapi/queryPriceRule", nil)
	// req.Close = true
	if err != nil {
		fmt.Println("create req err:", err)
		return
	}
	for {
		go newRequest(client, req)
		time.Sleep(time.Second / time.Duration(*requestPerSecond) / 6)

		sleepCounter += 1
		if sleepCounter >= *requestPerSecond {
			timeElapsed := time.Since(timeStart)
			fmt.Printf("Create %d requests, cost time %v\n", sleepCounter, timeElapsed)
			if timeElapsed < time.Second {
				time.Sleep(time.Second - timeElapsed)
			}

			timeStart = time.Now()
			sleepCounter = 0
		}
	}
}
