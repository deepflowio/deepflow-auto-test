package http2

import (
	"bytes"
	"crypto/tls"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"time"

	uuid "github.com/satori/go.uuid"

	"golang.org/x/net/http2"
)

type Http2Client struct {
	isReady bool
	req     *http.Request
	reqBody io.ReadCloser

	LatencyChan    chan *time.Duration
	ErrLatencyChan chan *time.Duration

	Addr       string
	Client     *http.Client
	Method     string
	Complexity int
	DataSize   int
	KeepAlive  bool
}

func (hc *Http2Client) InitClient() {
	var err error
	if hc.Method == "" {
		hc.Method = "GET"
	}
	hc.Client = &http.Client{
		// Skip TLS dial
		Transport: &http2.Transport{
			AllowHTTP: true,
			DialTLS: func(network, addr string, cfg *tls.Config) (net.Conn, error) {
				return net.Dial(network, addr)
			},
		},
	}
	// body size
	hc.reqBody = io.NopCloser(bytes.NewReader(bytes.Repeat([]byte("A"), hc.DataSize)))

	hc.req, err = http.NewRequest(hc.Method, hc.Addr, hc.reqBody)

	if err != nil {
		log.Fatal(fmt.Errorf("error making request: %v", err))
	}
	// set headers by Complexity
	for i := 0; i < hc.Complexity; i++ {
		hc.req.Header.Set(fmt.Sprintf("token%d", i), uuid.NewV1().String())
	}

	hc.req.ContentLength = int64(hc.DataSize)
	if hc.KeepAlive == true {
		resp, err := hc.Client.Do(hc.req)
		if err != nil {
			log.Fatal(fmt.Errorf("error do request: %v", err))
		}
		defer resp.Body.Close()
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			log.Fatalf("Read Response Error: %s", err)
		}
		fmt.Printf("Get Response %d length: %d\n", resp.StatusCode, len(body))
	} else {
		//hc.req.Header.Add("Connection", "close")
		//hc.req.Close = true
	}
	hc.isReady = true
}

func (hc *Http2Client) IsReady() bool {
	return hc.isReady
}

func (hc *Http2Client) Exec() error {
	hc.Get()
	return nil
}

func (hc *Http2Client) Get() {
	// set headers by Complexity
	req, _ := http.NewRequest(hc.Method, hc.Addr, hc.reqBody)
	for i := 0; i < hc.Complexity; i++ {
		newUuid := uuid.NewV1().String()
		req.Header.Set(fmt.Sprintf("token%s", newUuid), newUuid)
	}
	start := time.Now()
	resp, err := hc.Client.Do(req)
	latency := time.Since(start)
	if err != nil {
		hc.ErrLatencyChan <- &latency
		fmt.Println("query error:", err)
	} else {
		hc.LatencyChan <- &latency
	}
	defer resp.Body.Close()

	// body, err := io.ReadAll(resp.Body)
	// if err != nil {
	// 	log.Fatalf("Read Response Error: %s", err)
	// }
	// fmt.Printf("Get Response %d length: %d\n", resp.StatusCode, len(body))
}

func (hc *Http2Client) Close() {
	if hc.Client != nil {
		// hc.Client.Close()
		return
	}
}
