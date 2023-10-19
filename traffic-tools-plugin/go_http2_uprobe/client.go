package main

import (
    "context"
    "demo/go_http2_uprobe/pb"
    "fmt"
    "google.golang.org/grpc"
    "time"
    "os"
    "strconv"
)

var (
	newFlow      = 80
)

func newRequest(cli pb.DemoClient) {
    var i uint32 = 1
    cli.Call(context.TODO(), &pb.Req{
        Msg: &pb.Msg{
            ID:      i,
            Payload: []byte{1, 2, 3, 4},
        },
        Trace: &pb.Trace{
            TraceId: 999,
            Start:   999,
            Span:    123,
        },
    })
}

func main() {
    if len(os.Args) == 2{
		newFlow, _ = strconv.Atoi(os.Args[1])
	}
	sleepCounter := 0
	timeStart := time.Now()
    c, _ := grpc.Dial("127.0.0.1:1234", grpc.WithInsecure())
    cli := pb.NewDemoClient(c)
	for  {
		go newRequest(cli)
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