package redis

import (
	"fmt"

	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
	"github.com/go-redis/redis"
)

type RedisClient struct {
	lantencys []int
	count     int
	errs      int

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

func (rc *RedisClient) Exec() {
	return
}

func (rc *RedisClient) GetLantency() *common.LantencyResult {
	return nil
}

func (rc *RedisClient) Get() {
	_, err := rc.Client.Get("name").Result()
	if err != nil {
		fmt.Println(err)
	}
}

func (rc *RedisClient) Close() {
	if rc.Client != nil {
		rc.Client.Close()
	}
}
