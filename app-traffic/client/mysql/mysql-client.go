package mysql

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

type MysqlClient struct {
	values  []any
	isReady bool

	LatencyChan    chan *time.Duration
	ErrLatencyChan chan *time.Duration

	Addr         string
	Password     string
	User         string
	DB           string
	Client       *sql.DB
	SessionCount int
	Complexity   int
	Sql          string
}

func (mc *MysqlClient) Property() {
	log.Println("MySqlClient Property:")
	log.Printf("Addr: %s\n", mc.Addr)
	log.Printf("User: %s\n", mc.User)
	log.Printf("Password: %s\n", mc.Password)
	log.Printf("DB: %s\n", mc.DB)
	log.Printf("SessionCount: %d\n", mc.SessionCount)
	log.Printf("Complexity: %d\n", mc.Complexity)
	log.Printf("Sql: %s\n", mc.Sql)
}

// InitClient 初始化MySQL客户端连接。
// 此方法会首先尝试创建数据库（如果不存在），然后创建数据库连接，并设置最大连接数和最大空闲连接数。
// 还会执行一个查询SQL来准备客户端操作。
func (mc *MysqlClient) InitClient() {
	// 如果数据库名称未设置，则默认为"app_traffic_test"
	var err error
	if mc.DB == "" {
		mc.DB = "app_traffic_test"
	}
	// 构造数据库连接字符串
	dataSourceName := fmt.Sprintf("%s:%s@tcp(%s)/", mc.User, mc.Password, mc.Addr)
	// 尝试打开数据库连接
	db, _ := sql.Open("mysql", dataSourceName)
	// 创建数据库，如果不存在
	_, err = db.Exec(fmt.Sprintf("CREATE DATABASE IF NOT EXISTS %s", mc.DB))
	if err != nil {
		log.Fatal("create DB error:", err)
	}
	db.Close() // 关闭临时数据库连接

	// 打开应用程序使用的数据库连接，并设置最大连接数和最大空闲连接数
	mc.Client, err = sql.Open("mysql", mc.User+":"+mc.Password+"@tcp("+mc.Addr+")/"+mc.DB)
	if err != nil {
		log.Fatal("create DB error:", err)
	}
	mc.Client.SetMaxOpenConns(mc.SessionCount) // 设置最大连接数
	mc.Client.SetMaxIdleConns(mc.SessionCount) // 设置保留连接数

	// 准备查询SQL并执行
	mc.Sql = mc.getQuerySQL()
	rows, err := mc.Client.Query(mc.Sql)
	if err != nil {
		panic(err)
	}
	defer rows.Close()          // 确保查询结果被关闭
	cols, err := rows.Columns() // 获取查询结果的列名
	if err != nil {
		panic(err)
	}
	// 初始化存储查询结果的切片
	mc.values = make([]any, len(cols))
	data := make([][]byte, len(cols))

	// 为每一列创建一个字节切片，并将其地址赋值给values切片
	for i := range mc.values {
		mc.values[i] = &data[i]
	}
	mc.isReady = true // 标记客户端为就绪状态
}

func (mc *MysqlClient) IsReady() bool {
	return mc.isReady
}

func (mc *MysqlClient) Exec() error {
	err := mc.QueryTest()
	return err
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

// QueryTest 是 MysqlClient 类的一个方法，用于并发执行查询操作，并统计每个查询的延迟时间。
// 该方法不接受参数，返回可能发生的错误。
func (mc *MysqlClient) QueryTest() error {
	var err error
	rows := make([]*sql.Row, mc.SessionCount)          // 创建一个存储查询结果行的切片
	latencys := make([]time.Duration, mc.SessionCount) // 创建一个切片来存储每个查询的延迟时间

	// 并发执行查询操作，并记录每次查询的延迟时间
	for i := 0; i < mc.SessionCount; i++ {
		start := time.Now()
		rows[i] = mc.Client.QueryRow(mc.Sql) // 执行查询
		latency := time.Since(start)         // 计算查询延迟
		latencys[i] = latency
	}

	// 对每个查询结果进行处理，统计总延迟时间，并处理可能发生的错误
	for i := 0; i < mc.SessionCount; i++ {
		start := time.Now()
		err := rows[i].Scan(mc.values...)   // 提取查询结果
		latency := time.Since(start)        // 计算处理延迟
		sumLatency := latencys[i] + latency // 计算总延迟时间
		if err != nil {
			mc.ErrLatencyChan <- &sumLatency       // 如果有错误，将总延迟时间发送到错误延迟通道
			fmt.Println("sql query error 1:", err) // 打印查询错误信息
		} else {
			mc.LatencyChan <- &sumLatency // 无错误，将总延迟时间发送到正常延迟通道
		}
	}

	return err
}
