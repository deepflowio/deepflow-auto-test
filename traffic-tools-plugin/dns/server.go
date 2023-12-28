package main

import (
	"fmt"
	"golang.org/x/net/dns/dnsmessage"
	"net"
	"sync/atomic"
	"time"
)

func main() {
	// 设置 DNS 服务器监听地址
	serverAddr := "0.0.0.0:19053"
	totalPacket := uint64(0)
	// 创建 UDP 连接
	udpAddr, err := net.ResolveUDPAddr("udp", serverAddr)
	if err != nil {
		fmt.Printf("Error resolving address: %v\n", err)
		return
	}
	conn, err := net.ListenUDP("udp", udpAddr)
	if err != nil {
		fmt.Printf("Error creating UDP listener: %v\n", err)
		return
	}
	defer conn.Close()
	fmt.Printf("DNS server is listening on %s\n", serverAddr)

	go func() {
		for {
			buffer := make([]byte, 512)
			_, addr, err := conn.ReadFromUDP(buffer)
			if err != nil {
				fmt.Printf("Error reading from UDP: %v\n", err)
				continue
			}
			atomic.AddUint64(&totalPacket, 1)
			// 解析 DNS 查询请求
			var request dnsmessage.Message
			request.Unpack(buffer)

			// 构建 DNS 响应消息
			response := dnsmessage.Message{
				Header: dnsmessage.Header{
					ID:       request.Header.ID, // 使用相同的事务 ID
					Response: true,              // 设置为响应
				},
				Questions: request.Questions, // 复制查询问题
				Answers: []dnsmessage.Resource{
					{
						Header: dnsmessage.ResourceHeader{
							Name:  request.Questions[0].Name, // 使用相同的查询域名
							Type:  dnsmessage.TypeA,          // 响应类型，A表示 IPv4 地址
							Class: dnsmessage.ClassINET,      // 查询类别，通常是 INET
							TTL:   300,                       // TTL (Time to Live) 设置为 300 秒
						},
						Body: &dnsmessage.AResource{
							A: [4]byte{192, 168, 1, 100}, // 设置响应的 IP 地址
						},
					},
				},
			}
			responseData, _ := response.Pack()
			conn.WriteToUDP(responseData, addr)
		}
	}()

	ticker := time.NewTicker(1 * time.Second)
	i := 0
	for range ticker.C {
		i += 1
		fmt.Printf("%s %d totalPacket %d,\n",
			time.Now().Format(time.RFC3339), i, atomic.LoadUint64(&totalPacket))
	}

}
