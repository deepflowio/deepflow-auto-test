package mongo

import (
	"fmt"
	"log"
	"time"

	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

type MongoClient struct {
	lantencys []*time.Duration
	count     int
	errCount  int
	isReady   bool

	collection *mgo.Collection

	Addr       string
	Password   string
	DB         string
	Client     *mgo.Session
	StartTime  time.Time
	Complexity int
}

func (mc *MongoClient) InitClient() {
	var err error
	if mc.DB == "" {
		mc.DB = "app_traffic_test"
	}
	mc.Client, err = mgo.Dial(mc.Addr)
	if err != nil {
		log.Fatal(err)
	}
	mc.collection = mc.Client.DB(mc.DB).C("test")
	_, err = mc.collection.RemoveAll(bson.M{})
	if err != nil {
		log.Fatal(err)
	}
	// init data needed by get func

	builder := common.NewBuilder()
	for i := 0; i < mc.Complexity; i++ {
		builder = builder.AddString(fmt.Sprintf("Key%d", i))
	}
	newStruct := builder.Build().New()
	for i := 0; i < mc.Complexity; i++ {
		newStruct.SetString(fmt.Sprintf("Key%d", i), fmt.Sprintf("value%d", i))
	}

	err = mc.collection.Insert(newStruct.Addr())
	if err != nil {
		log.Fatal(err)
	}
	mc.isReady = true
}

func (mc *MongoClient) IsReady() bool {
	return mc.isReady
}

func (mc *MongoClient) Exec() error {
	mc.Get()
	return nil
}

func (mc *MongoClient) Get() {
	start := time.Now()
	var result []bson.M
	err := mc.collection.Find(nil).All(&result)
	lantency := time.Since(start)
	mc.lantencys = append(mc.lantencys, &lantency)
	if err != nil {
		mc.errCount += 1
		fmt.Println("query error:", err)
	} else {
		mc.count += 1
	}
}

func (mc *MongoClient) Close() {
	if mc.Client != nil {
		mc.Client.Close()
	}
}

func (mc *MongoClient) GetCount() int {
	return mc.count
}

func (mc *MongoClient) GetErrCount() int {
	return mc.errCount
}

func (mc *MongoClient) GetLantency() (lr *common.LantencyResult) {
	lr = &common.LantencyResult{
		Lantencys: mc.lantencys,
		Count:     mc.count,
		ErrCount:  mc.errCount,
	}
	return lr
}
