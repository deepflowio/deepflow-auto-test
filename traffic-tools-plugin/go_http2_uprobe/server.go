package main

import (
    "context"
    "demo/go_http2_uprobe/pb"
    "fmt"
    "google.golang.org/grpc"
    "net"
)

type demoServer struct{}

func (s *demoServer) Call(ctx context.Context, req *pb.Req) (*pb.Resp, error) {
    return &pb.Resp{
        Msg: req.Msg,
        Trace: &pb.Trace{
            TraceId: 999,
            Start:   999,
            Span:    123,
        },
    }, nil
}

func main() {
    s := grpc.NewServer()
    pb.RegisterDemoServer(s, &demoServer{})
    l, err := net.Listen("tcp", ":1234")
    if err != nil {
        panic(err)
    }
    fmt.Println("Server is running on :1234")
    panic(s.Serve(l))
}
