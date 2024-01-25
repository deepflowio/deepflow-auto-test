package redis

import (
	"fmt"
	"time"

	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
	"github.com/go-redis/redis"
)

type RedisClient struct {
	lantencys []time.Duration
	count     int
	errCount  int

	Addr     string
	Password string
	DB       int
	Client   *redis.Client
}

func (rc *RedisClient) InitClient() {
	client := redis.NewClient(&redis.Options{
		Addr:     rc.Addr,     // redis地址
		Password: rc.Password, // 密码
		DB:       rc.DB,       // 使用默认数据库
	})
	rc.Client = client
}

func (rc *RedisClient) Exec() error {
	rc.get()
	return nil
}

func (rc *RedisClient) GetCount() int {
	return rc.count
}

func (rc *RedisClient) GetErrCount() int {
	return rc.errCount
}

func (rc *RedisClient) GetLantency() *common.LantencyResult {
	return nil
}

func (rc *RedisClient) set() {
	start := time.Now()
	err := rc.Client.Set("name", "john", 0).Err()
	lantency := time.Since(start)
	rc.lantencys = append(rc.lantencys, lantency)
	if err != nil {
		rc.errCount += 1
		fmt.Println(err)
	} else {
		rc.count += 1
	}
}

func (rc *RedisClient) get() {
	start := time.Now()
	_, err := rc.Client.Get("name").Result()
	lantency := time.Since(start)
	rc.lantencys = append(rc.lantencys, lantency)
	if err != nil {
		rc.errCount += 1
		fmt.Println(err)
	} else {
		rc.count += 1
	}
}

func (rc *RedisClient) Close() {
	if rc.Client != nil {
		rc.Client.Close()
	}
}
