package client

type EngineClient interface {
	Exec() error
	InitClient()
	Close()
	IsReady() bool
	Property()
}
