package client

type Client interface {
	Exec() error
	GetLantency() *LantencyResult
	GetCount() *int
	GetErrCount() *int
}
