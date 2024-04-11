package http

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

type HttpClient struct {
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
	TLS        bool
	H2C        bool
}

func (hc *HttpClient) Property() {
	log.Println("HttpClient Property:")
	log.Printf("Addr: %s\n", hc.Addr)
	log.Printf("Method: %s\n", hc.Method)
	log.Printf("Complexity: %d\n", hc.Complexity)
	log.Printf("DataSize: %d\n", hc.DataSize)
	log.Printf("KeepAlive: %t\n", hc.KeepAlive)
	log.Printf("TLS: %t\n", hc.TLS)
	log.Printf("H2C: %t\n", hc.H2C)
}

// InitClient 初始化HttpClient。
// 此函数配置HTTP请求的方法、客户端类型、请求体大小、请求头等，并准备执行HTTP请求。
// 对于不同的配置，会创建相应的http.Client实例以支持HTTP/2连接或TLS连接。
// 在请求完成后，根据是否保持连接的设置，可能打印响应状态码和响应体长度。
func (hc *HttpClient) InitClient() {
	var err error
	if hc.Method == "" {
		hc.Method = "GET" // 默认请求方法为GET
	}

	disableKeepAlives := false
	if !hc.KeepAlive {
		disableKeepAlives = true
	}

	if hc.H2C {
		// 使用HTTP/2客户端，跳过TLS握手
		hc.Client = &http.Client{
			Transport: &http2.Transport{
				AllowHTTP: true,
				DialTLS: func(network, addr string, cfg *tls.Config) (net.Conn, error) {
					// 直接建立TCP连接，不进行TLS握手
					return net.Dial(network, addr)
				},
			},
		}
	} else {
		if hc.TLS {
			// 使用支持TLS的HTTP客户端，且不验证TLS证书
			hc.Client = &http.Client{
				Transport: &http.Transport{
					TLSClientConfig:   &tls.Config{InsecureSkipVerify: true},
					DisableKeepAlives: disableKeepAlives,
					DialContext: (&net.Dialer{
						Timeout:   30 * time.Second, // 连接超时时间
						KeepAlive: 60 * time.Second, // 保持长连接的时间
					}).DialContext, // 设置连接的参数
					MaxIdleConns:          500,              // 最大空闲连接
					IdleConnTimeout:       60 * time.Second, // 空闲连接的超时时间
					ExpectContinueTimeout: 30 * time.Second, // 等待服务第一个响应的超时时间
					MaxIdleConnsPerHost:   100,              // 每个host保持的空闲连接数
				},
			}
		} else {
			// 使用默认的HTTP客户端
			hc.Client = &http.Client{
				Transport: &http.Transport{
					DisableKeepAlives: disableKeepAlives, // 使用长连接
					DialContext: (&net.Dialer{
						Timeout:   30 * time.Second, // 连接超时时间
						KeepAlive: 60 * time.Second, // 保持长连接的时间
					}).DialContext, // 设置连接的参数
					MaxIdleConns:          500,              // 最大空闲连接
					IdleConnTimeout:       60 * time.Second, // 空闲连接的超时时间
					ExpectContinueTimeout: 30 * time.Second, // 等待服务第一个响应的超时时间
					MaxIdleConnsPerHost:   100,              // 每个host保持的空闲连接数
				},
			}
		}
	}

	// 创建请求体，其大小由hc.DataSize指定
	hc.reqBody = io.NopCloser(bytes.NewReader(bytes.Repeat([]byte("A"), hc.DataSize)))

	// 创建HTTP请求
	hc.req, err = http.NewRequest(hc.Method, hc.Addr, hc.reqBody)
	if err != nil {
		// 处理创建请求失败的情况
		log.Fatal(fmt.Errorf("error making request: %v", err))
	}

	// 根据复杂度设置请求头
	for i := 0; i < hc.Complexity; i++ {
		hc.req.Header.Set(fmt.Sprintf("token%d", i), uuid.NewV1().String())
	}

	hc.req.ContentLength = int64(hc.DataSize) // 设置请求体内容长度
	if hc.KeepAlive{
		// 执行HTTP请求，并处理响应
		resp, err := hc.Client.Do(hc.req)
		if err != nil {
			// 处理请求执行失败的情况
			log.Fatal(fmt.Errorf("error do request: %v", err))
		}
		defer resp.Body.Close() // 确保响应体关闭
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			// 处理读取响应体失败的情况
			log.Fatalf("Read Response Error: %s", err)
		}
		// 打印响应状态码和响应体长度
		fmt.Printf("Get Response %d length: %d\n", resp.StatusCode, len(body))
	}
	hc.isReady = true // 标记客户端为准备就绪状态
}

func (hc *HttpClient) IsReady() bool {
	return hc.isReady
}

func (hc *HttpClient) Exec() error {
	hc.Get()
	return nil
}

func (hc *HttpClient) Get() {
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
	// 用于复用连接
	io.ReadAll(resp.Body)
	defer resp.Body.Close()

}

func (hc *HttpClient) Close() {
	if hc.Client != nil {
		// hc.Client.Close()
		return
	}
}
