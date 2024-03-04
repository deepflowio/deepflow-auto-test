package grpc

import (
	"context"
	pb "github.com/deepflowio/deepflow-auto-test/app-traffic/client/grpc/pb"
	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"log"
	"time"
)
//go:generate  mkdir ./pb
//go:generate  protoc --go_out=./pb --go_opt=paths=source_relative --go-grpc_out=./pb --go-grpc_opt=paths=source_relative pb.proto
type GrpcClient struct {
	lantencys []*time.Duration
	count     int
	errCount  int

	Addr      string
	Client    pb.GreeterClient
	StartTime time.Time
	Conn      *grpc.ClientConn
}

func (gc *GrpcClient) InitClient() {
	conn, err := grpc.Dial(gc.Addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("connect failed: %v", err)
	}
	gc.Conn = conn
	gc.Client = pb.NewGreeterClient(conn)
	gc.StartTime = time.Now()

}
func (gc *GrpcClient) Close() {
	if gc.Client != nil {
		gc.Conn.Close()
	}
}
func (gc *GrpcClient) Exec() error {
	start := time.Now()
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	_, err := gc.Client.SayHello(ctx, &pb.HelloRequest{
		Name1: "hello",Name2: "hello",Name3: "hello",Name4: "hello",
		Name5: "hello",Name6: "hello",Name7: "hello",Name8: "hello",
		Name9: "hello",Name10: "hello",
	})
	lantency := time.Since(start)
	gc.lantencys = append(gc.lantencys, &lantency)
	if err != nil {
		gc.errCount += 1
		log.Printf("unable to send message: %v", err)
	} else {
		gc.count += 1
	}
	return err
}

func (gc *GrpcClient) GetCount() int {
	return gc.count
}

func (gc *GrpcClient) GetErrCount() int {
	return gc.errCount
}

func (gc *GrpcClient) GetLantency() (lr *common.LantencyResult) {
	lr = &common.LantencyResult{
		Lantencys: gc.lantencys,
		Count:     gc.count,
		ErrCount:  gc.errCount,
	}
	return lr
}
