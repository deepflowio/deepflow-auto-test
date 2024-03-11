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
	values    []any
	isReady   bool

	Addr         string
	Password     string
	User         string
	DB           string
	Client       *sql.DB
	StartTime    time.Time
	SessionCount int
	Complexity   int
	Sql          string
}

func (mc *MysqlClient) InitClient() {
	var err error
	if mc.DB == "" {
		mc.DB = "app_traffic_test"
	}
	dataSourceName := fmt.Sprintf("%s:%s@tcp(%s)/", mc.User, mc.Password, mc.Addr)
	db, _ := sql.Open("mysql", dataSourceName)
	_, err = db.Exec(fmt.Sprintf("CREATE DATABASE IF NOT EXISTS %s", mc.DB))
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

	mc.Sql = mc.getQuerySQL()
	rows, err := mc.Client.Query(mc.Sql)
	if err != nil {
		panic(err)
	}
	defer rows.Close()
	cols, err := rows.Columns()
	if err != nil {
		panic(err)
	}
	mc.values = make([]any, len(cols))
	data := make([][]byte, len(cols))

	// 将字节切片地址赋值给空接口切片
	for i := range mc.values {
		mc.values[i] = &data[i]
	}
	mc.isReady = true
}

func (mc *MysqlClient) IsReady() bool {
	return mc.isReady
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

func (mc *MysqlClient) getQuerySQL() (sql string) {
	if mc.Sql != "" {
		return mc.Sql
	}
	sql = "SELECT 0"
	for i := 1; i < mc.Complexity; i++ {
		sql = fmt.Sprintf("%s, %d", sql, i)
	}
	return sql
}

func (mc *MysqlClient) QueryTest() error {
	var err error
	rows := make([]*sql.Row, mc.SessionCount)
	lanLen := len(mc.lantencys)
	for i := 0; i < mc.SessionCount; i++ {
		start := time.Now()
		rows[i] = mc.Client.QueryRow(mc.Sql)
		//rows[i], err = mc.Client.Query("SELECT 1")
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
		start := time.Now()
		err := rows[i].Scan(mc.values...)
		lantency := time.Since(start)
		sumLantency := *mc.lantencys[lanLen+i] + lantency
		mc.lantencys[lanLen+i] = &sumLantency
		if err != nil {
			mc.errCount += 1
			mc.count -= 1
			fmt.Println("sql query error:", err)
		}
	}
	return err
}
