package grpc

import (
	"context"
	"log"
	"time"

	pb "github.com/deepflowio/deepflow-auto-test/app-traffic/client/grpc/pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

//go:generate  mkdir ./pb
//go:generate  protoc --go_out=./pb --go_opt=paths=source_relative --go-grpc_out=./pb --go-grpc_opt=paths=source_relative pb.proto
type GrpcClient struct {
	isReady bool

	LatencyChan    chan *time.Duration
	ErrLatencyChan chan *time.Duration

	Addr   string
	Client pb.GreeterClient
	Conn   *grpc.ClientConn
}

func (gc *GrpcClient) Property() {
	log.Printf("GrpcClient Property:")
	log.Printf("Addr: %s", gc.Addr)
}

func (gc *GrpcClient) InitClient() {
	conn, err := grpc.Dial(gc.Addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("connect failed: %v", err)
	}
	gc.Conn = conn
	gc.Client = pb.NewGreeterClient(conn)
	gc.isReady = true
}

func (gc *GrpcClient) IsReady() bool {
	return gc.isReady
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
		Name1: "hello", Name2: "hello", Name3: "hello", Name4: "hello",
		Name5: "hello", Name6: "hello", Name7: "hello", Name8: "hello",
		Name9: "hello", Name10: "hello",
	})
	latency := time.Since(start)
	if err != nil {
		gc.ErrLatencyChan <- &latency
		log.Printf("unable to send message: %v", err)
	} else {
		gc.LatencyChan <- &latency
	}
	return err
}
