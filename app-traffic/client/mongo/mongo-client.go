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
	isReady    bool
	collection *mgo.Collection

	LatencyChan    chan *time.Duration
	ErrLatencyChan chan *time.Duration

	Addr       string
	Password   string
	DB         string
	Client     *mgo.Session
	Complexity int
}

func (mc *MongoClient) Property() {
	fmt.Printf("MongoClient Property: \n")
	fmt.Printf("Addr: %s\n", mc.Addr)
	fmt.Printf("DB: %s\n", mc.DB)
	fmt.Printf("Complexity: %d\n", mc.Complexity)
}

func (mc *MongoClient) InitClient() {
	var err error
	if mc.DB == "" {
		mc.DB = "app_traffic_test"
	}
	mc.Client, err = mgo.Dial(mc.Addr)
	if err != nil {
		log.Fatal(fmt.Sprintf("Dial Addr %s Err: %v", mc.Addr, err))
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
	latency := time.Since(start)
	if err != nil {
		mc.ErrLatencyChan <- &latency
		fmt.Println("query error:", err)
	} else {
		mc.LatencyChan <- &latency
	}
}

func (mc *MongoClient) Close() {
	if mc.Client != nil {
		mc.Client.Close()
	}
}
