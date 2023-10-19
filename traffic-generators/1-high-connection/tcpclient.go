package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"strconv"
	"strings"
	"syscall"
	"time"
	"sync/atomic"
)

const (
	MIN_SERVER_PORT  = 20000
	MAX_SERVER_PORT  = 24999
	NEW_FLOW_PER_SEC = 3000

	REQUEST_PER_FLOW = 1
	REQUEST_INTERVAL = 1 * time.Second

	L7_PROTOCOL_UNKNOWN = 1
	L7_PROTOCOL_HTTP    = 2
)

var (
	liveConnection     = int64(0)
	maxConcurrent      = 100000
	l7Protocol         = L7_PROTOCOL_UNKNOWN
	httpRequestPayload = `GET /index.html HTTP/1.1
Host: high-connection-load-generator
User-Agent: golang
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive

EOF
`
)

func setLimit() {
	var rLimit syscall.Rlimit
	if err := syscall.Getrlimit(syscall.RLIMIT_NOFILE, &rLimit); err != nil {
		panic(err)
	}
	rLimit.Cur = rLimit.Max
	if err := syscall.Setrlimit(syscall.RLIMIT_NOFILE, &rLimit); err != nil {
		panic(err)
	}

	fmt.Printf("set cur limit: %d\n", rLimit.Cur)
}

func newConnection(dialer *net.Dialer, serverIp string, serverPort int) {
	atomic.AddInt64(&liveConnection, 1)
	startTime := time.Now()

	conn, err := dialer.Dial("tcp", serverIp+":"+strconv.Itoa(serverPort))
	if err != nil {
		fmt.Printf("Dial server #%d from %s failed ...: %s\n", serverPort, dialer.LocalAddr, err.Error())
		return
	}
	defer conn.Close()
	// fmt.Printf("Request %d: local %s, remote %s\n", serverPort, conn.LocalAddr(), conn.RemoteAddr())
	reader := bufio.NewReader(conn)
	for i := 0; i < REQUEST_PER_FLOW; i++ {
		// read in input from stdin
		//reader := bufio.NewReader(os.Stdin)
		//fmt.Print("Text to send: ")
		//text, _ := reader.ReadString('\n')

		// send to socket
		msg := ""
		if l7Protocol == L7_PROTOCOL_HTTP {
			msg = httpRequestPayload
		} else {
			msg = "#" + strconv.Itoa(serverPort) + "-" + strconv.Itoa(i) + "\n"
		}
		_, err = fmt.Fprintf(conn, msg)
		if err != nil {
			fmt.Printf("Flow %s->#%d write (%d/%d, %v) failed ...: %s\n",
				dialer.LocalAddr, serverPort, i+1, REQUEST_PER_FLOW, time.Since(startTime), err.Error())
			break
		}

		// listen for reply
		if l7Protocol == L7_PROTOCOL_UNKNOWN {
			msg, err = reader.ReadString('\n')
			if err != nil {
				fmt.Printf("Flow %s->#%d read (%d/%d, %v) failed ...: %s\n",
					dialer.LocalAddr, serverPort, i+1, REQUEST_PER_FLOW, time.Since(startTime), err.Error())
				break
			}
		} else {
			for msg != "EOF\n" {
				msg, err = reader.ReadString('\n')
				if err != nil {
					fmt.Printf("Flow %s->#%d read (%d/%d, %v) failed ...: %s\n",
						dialer.LocalAddr, serverPort, i+1, REQUEST_PER_FLOW, time.Since(startTime), err.Error())
					break
				}
			}
		}
		// fmt.Print("Message from server: " + message)

		time.Sleep(REQUEST_INTERVAL / 10)
	}
	atomic.AddInt64(&liveConnection, -1)
	// fmt.Printf("Finished %d: local %s, remote %s\n", serverPort, conn.LocalAddr(), conn.RemoteAddr())
}

func main() {
	if len(os.Args) != 3 && len(os.Args) != 4 {
		fmt.Printf("./tcpclient concurrent remote_addr_1,remote_addr_2,... [local_addr_1,local_addr_2...]")
		return
	}
	setLimit()
	maxConcurrent, _ = strconv.Atoi(os.Args[1])
	serverIps := strings.Split(os.Args[2], ",")
	clientIps := []string{}
	if len(os.Args) == 3 {
		fmt.Printf("Dail %s\n", serverIps)
	} else {
		clientIps = strings.Split(os.Args[3], ",")
		fmt.Printf("Dail %s from %s\n", serverIps, clientIps)
	}

	sleepCounter := 0
	timeStart := time.Now()

	dialer := &net.Dialer{}
	clientIpIndex := 0
	serverIpIndex := 0
	if len(clientIps) > 0 {
		dialer = &net.Dialer{
			LocalAddr: &net.TCPAddr{IP: net.ParseIP(clientIps[clientIpIndex])},
		}
	}

	for serverPort := MIN_SERVER_PORT; ; serverPort++ {
		if  atomic.LoadInt64(&liveConnection) + 1 > int64(maxConcurrent){
			time.Sleep(time.Second)
			timeStart = time.Now()
			sleepCounter = 0
			continue
		}
		if serverPort > MAX_SERVER_PORT {
			serverPort = MIN_SERVER_PORT
			if len(clientIps) > 0 {
				clientIpIndex = (clientIpIndex + 1) % len(clientIps)
				dialer = &net.Dialer{
					LocalAddr: &net.TCPAddr{IP: net.ParseIP(clientIps[clientIpIndex])},
				}
			}
			if clientIpIndex == 0 {
				serverIpIndex = (serverIpIndex + 1) % len(serverIps)
			}
		}
		go newConnection(dialer, serverIps[serverIpIndex], serverPort)
		time.Sleep(time.Second / NEW_FLOW_PER_SEC / 3000)

		sleepCounter += 1
		if sleepCounter >= NEW_FLOW_PER_SEC {
			timeElapsed := time.Since(timeStart)
			fmt.Printf("Create %d connections, clientIp %s, serverIp %s, serverport %d-%d ~ %d, cost %v, curConnections:%d\n",
				sleepCounter, clientIps[clientIpIndex], serverIps[serverIpIndex],
				serverPort, sleepCounter, serverPort, timeElapsed, atomic.LoadInt64(&liveConnection))
			if timeElapsed < time.Second {
				time.Sleep(time.Second - timeElapsed)
			}

			timeStart = time.Now()
			sleepCounter = 0
		}
	}
}
