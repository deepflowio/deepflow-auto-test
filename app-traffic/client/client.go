package client

import (
	"github.com/deepflowio/deepflow-auto-test/app-traffic/common"
)

type EngineClient interface {
	Exec() error
	InitClient()
	GetLantency() *common.LantencyResult
	GetCount() int
	GetErrCount() int
	Close()
}
