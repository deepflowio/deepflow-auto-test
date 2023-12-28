package main

import (
	"flag"
	"fmt"
	"golang.org/x/net/dns/dnsmessage"
	"net"
	"time"
)

var (
	request_per_conn = flag.Int("r", 10, "Number of requests per connection")
	concurrentConn   = flag.Int("c", 1, "Number of concurrent connections")
	request_interval = time.Second / 10
)

func newConnection(queryData []byte) {
	flag.Parse()
	serverAddr := "127.0.0.1:19053"

	// 创建 UDP 连接到 DNS 服务器
	udpAddr, err := net.ResolveUDPAddr("udp", serverAddr)
	if err != nil {
		fmt.Printf("Error resolving address: %v\n", err)
	}
	conn, err := net.DialUDP("udp", nil, udpAddr)
	if err != nil {
		fmt.Printf("Error creating UDP connection: %v\n", err)
	}
	defer conn.Close()
	for i := 0; i < *request_per_conn; i++ {
		conn.Write(queryData)
		responseData := make([]byte, 512)
		conn.Read(responseData)
		time.Sleep(request_interval)
	}
}

func main() {

	message := dnsmessage.Message{
		Header: dnsmessage.Header{
			ID:               12345,
			Response:         false,
			OpCode:           0,
			RecursionDesired: true,
		},
		Questions: []dnsmessage.Question{
			{
				Name:  dnsmessage.MustNewName("baidu.com."),
				Type:  dnsmessage.TypeA,
				Class: dnsmessage.ClassINET,
			},
		},
	}
	// 编码 DNS 查询消息
	queryData, err := message.Pack()
	if err != nil {
		fmt.Printf("Failed to encode DNS query: %v\n", err)
	}
	sleepCounter := 0
	timeStart := time.Now()

	for {
		go newConnection(queryData)
		time.Sleep(time.Second / time.Duration(*concurrentConn) / 6)

		sleepCounter += 1
		if sleepCounter >= *concurrentConn {
			timeElapsed := time.Since(timeStart)
			if timeElapsed < time.Second {
				fmt.Printf("Create %d connections\n", sleepCounter)
				time.Sleep(time.Second - timeElapsed)
			}

			timeStart = time.Now()
			sleepCounter = 0
		}
	}

}
