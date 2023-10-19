package main

import (
	"fmt"
	"os"
	"net/http"
	"io/ioutil"
	"strconv"
	"time"
)

const (
	SERVER_PORT  = 8080
	REQUEST_INTERVAL = time.Second 
)

var (
	newFlow    = 80
	serverIp   = ""
)

func newRequest(client *http.Client,req *http.Request)  {

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
	if len(os.Args) == 2{
		newFlow, _ = strconv.Atoi(os.Args[1])
	}
	ipAddress := "http://127.0.0.1:8080"
	sleepCounter := 0
	timeStart := time.Now()
	transport := &http.Transport{
		MaxIdleConns:        100, 
		MaxIdleConnsPerHost: 100, 
	}
	client := &http.Client{
		Transport: transport,
		Timeout: 100 * time.Second,
	}
	req, err := http.NewRequest("GET", ipAddress+"/v1/vtaps/", nil)
    if err != nil {
        fmt.Println("create req err:", err)
        return
    }

	for  {
		go newRequest(client, req)
		time.Sleep(time.Second / time.Duration(newFlow) / 6)

		sleepCounter += 1
		if sleepCounter >= newFlow {
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