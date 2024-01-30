package mysql

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
	_ "github.com/go-sql-driver/mysql"
)

type MysqlClient struct {
	lantencys []*time.Duration
	count     int
	errCount  int

	Addr         string
	Password     string
	User         string
	DB           string
	Client       *sql.DB
	StartTime    time.Time
	SessionCount int
}

func (mc *MysqlClient) InitClient() {
	var err error
	dataSourceName := fmt.Sprintf("%s:%s@tcp(%s)/", mc.User, mc.Password, mc.Addr)
	db, _ := sql.Open("mysql", dataSourceName)
	_, err = db.Exec("CREATE DATABASE IF NOT EXISTS app_traffic_test")
	if err != nil {
		log.Fatal("create DB error:", err)
	}
	db.Close()
	mc.Client, err = sql.Open("mysql", mc.User+":"+mc.Password+"@tcp("+mc.Addr+")/"+mc.DB)
	if err != nil {
		log.Fatal("create DB error:", err)
	}
	mc.Client.SetMaxOpenConns(mc.SessionCount) // 最大连接数
	mc.Client.SetMaxIdleConns(mc.SessionCount) // 保留连接数
	mc.StartTime = time.Now()
}

func (mc *MysqlClient) Exec() error {
	err := mc.QueryTest()
	return err
}

func (mc *MysqlClient) GetCount() int {
	return mc.count
}

func (mc *MysqlClient) GetErrCount() int {
	return mc.errCount
}

func (mc *MysqlClient) GetLantency() (lr *common.LantencyResult) {
	lr = &common.LantencyResult{
		Lantencys: mc.lantencys,
		Count:     mc.count,
		ErrCount:  mc.errCount,
	}
	return lr
}

func (mc *MysqlClient) Close() {
	if mc.Client != nil {
		mc.Client.Close()
	}
}
func (mc *MysqlClient) QueryTest() error {
	var err error
	rows := make([]*sql.Rows, mc.SessionCount)
	for i := 0; i < mc.SessionCount; i++ {
		start := time.Now()
		rows[i], err = mc.Client.Query("SELECT 1")
		lantency := time.Since(start)
		mc.lantencys = append(mc.lantencys, &lantency)
		if err != nil {
			mc.errCount += 1
			fmt.Println("sql query error:", err)
		} else {
			mc.count += 1
		}
	}
	for i := 0; i < mc.SessionCount; i++ {
		defer rows[i].Close()
	}
	return err
}
