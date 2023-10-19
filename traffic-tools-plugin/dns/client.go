package main

import (
	"fmt"
	"golang.org/x/net/dns/dnsmessage"
	"net"
	"os"
	"strconv"
	"time"
)
var (
	newFlow          = 1
	request_per_flow = 1
	request_interval = time.Second / 10

)
func newConnection(queryData []byte) {
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
	for i:=0; i < request_per_flow; i++{
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
	if len(os.Args) == 2{
		newFlow, _ = strconv.Atoi(os.Args[1])
	}
	if len(os.Args) == 3{
		newFlow, _ = strconv.Atoi(os.Args[1])
		request_per_flow, _ = strconv.Atoi(os.Args[2])
	}
	sleepCounter := 0
	timeStart := time.Now()

	for  {
		go newConnection(queryData)
		time.Sleep(time.Second / time.Duration(newFlow) / 6)

		sleepCounter += 1
		if sleepCounter >= newFlow {
			timeElapsed := time.Since(timeStart)
			if timeElapsed < time.Second {
				fmt.Printf("Create %d connections\n",sleepCounter)
				time.Sleep(time.Second - timeElapsed)
			}

			timeStart = time.Now()
			sleepCounter = 0
		}
	}

}