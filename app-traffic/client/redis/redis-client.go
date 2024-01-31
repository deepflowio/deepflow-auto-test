package redis

import (
	"fmt"
	"time"

	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
	"github.com/go-redis/redis"
)

type RedisClient struct {
	lantencys []*time.Duration
	count     int
	errCount  int
	keys      []string

	Addr       string
	Password   string
	DB         int
	Client     *redis.Client
	StartTime  time.Time
	Complexity int
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
	for i := 0; i < rc.Complexity; i++ {
		key := fmt.Sprintf("key%d", i)
		rc.keys[i] = key
	}
	rc.setMap()
	rc.StartTime = time.Now()
}

func (rc *RedisClient) setMap() {
	for i := 0; i < rc.Complexity; i++ {
		value := fmt.Sprintf("value%d", i)
		err := rc.Client.HSet("appHash", rc.keys[i], value).Err()
		if err != nil {
			fmt.Println("error: ", err)
		}
	}
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

func (rc *RedisClient) GetLantency() (lr *common.LantencyResult) {
	lr = &common.LantencyResult{
		Lantencys: rc.lantencys,
		Count:     rc.count,
		ErrCount:  rc.errCount,
	}
	return lr
}

func (rc *RedisClient) set() {
	start := time.Now()
	err := rc.Client.Set("name", "john", 0).Err()
	lantency := time.Since(start)
	rc.lantencys = append(rc.lantencys, &lantency)
	if err != nil {
		rc.errCount += 1
		fmt.Println("error: ", err)
	} else {
		rc.count += 1
	}
}

func (rc *RedisClient) get() {
	start := time.Now()
	_, err := rc.Client.HMGet("appHash", rc.keys...).Result()
	lantency := time.Since(start)
	rc.lantencys = append(rc.lantencys, &lantency)
	if err != nil {
		rc.errCount += 1
		fmt.Println("error: ", err)
	} else {
		rc.count += 1
	}
}

func (rc *RedisClient) Close() {
	if rc.Client != nil {
		rc.Client.Close()
	}
}
