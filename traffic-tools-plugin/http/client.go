package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

const (
	SERVER_PORT      = 8080
	REQUEST_INTERVAL = time.Second / 10
)

var (
	requestPerSecond = flag.Int("r", 100, "request per second")
)

func newRequest(client *http.Client, req *http.Request) {
	flag.Parse()
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
	req, err := http.NewRequest("GET", "http://localhost:8080/user_info?username=dftest&type=1", nil)
	if err != nil {
		fmt.Println("create req err:", err)
		return
	}

	jsonValue := `{"trace_id": "101", "span_id": "110"}`
	req.Header.Set("Custom-Trace-Info", jsonValue)

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
