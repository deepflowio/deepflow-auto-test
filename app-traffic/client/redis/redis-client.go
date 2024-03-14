package redis

import (
	"fmt"
	"strings"
	"time"

	"github.com/go-redis/redis"
)

type RedisClient struct {
	isReady bool

	LatencyChan    chan *time.Duration
	ErrLatencyChan chan *time.Duration

	keys []string
	hmap map[string]interface{}

	Addr       string
	Password   string
	DB         int
	Client     *redis.Client
	Complexity int
	Method     string
}

func (rc *RedisClient) InitClient() {
	client := redis.NewClient(&redis.Options{
		Addr:     rc.Addr,
		Password: rc.Password,
		DB:       rc.DB,
	})
	rc.Client = client
	// init data needed by get func
	rc.keys = make([]string, rc.Complexity)
	rc.hmap = make(map[string]interface{})
	for i := 0; i < rc.Complexity; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		rc.keys[i] = key
		rc.hmap[key] = value
	}
	rc.setMap()
	rc.isReady = true
}

func (rc *RedisClient) IsReady() bool {
	return rc.isReady
}

func (rc *RedisClient) setMap() error {
	return rc.Client.HMSet("appHash", rc.hmap).Err()
}

func (rc *RedisClient) Exec() error {
	if strings.ToUpper(rc.Method) == "SET" {
		rc.set()
	} else {
		rc.get()
	}
	return nil
}

func (rc *RedisClient) set() {
	start := time.Now()
	err := rc.setMap()
	latency := time.Since(start)
	if err != nil {
		rc.ErrLatencyChan <- &latency
		fmt.Println("error:", err)
	} else {
		rc.LatencyChan <- &latency
	}
}

func (rc *RedisClient) get() {
	start := time.Now()
	_, err := rc.Client.HMGet("appHash", rc.keys...).Result()
	latency := time.Since(start)
	if err != nil {
		rc.ErrLatencyChan <- &latency
		fmt.Println("error:", err)
	} else {
		rc.LatencyChan <- &latency
	}
}

func (rc *RedisClient) Close() {
	if rc.Client != nil {
		rc.Client.Close()
	}
}
