package common

import (
	"fmt"
	"sync"
	"time"

	"github.com/rcrowley/go-metrics"
)

type LatencyResult struct {
	Count       int
	ErrCount    int
	ExecSeconds float64

	h     metrics.Histogram
	mutex sync.Mutex
}

func (lr *LatencyResult) Init() {
	lr.h = metrics.NewHistogram(metrics.NewUniformSample(10000000))
	metrics.Register("latency.histogram", lr.h)
}

func (lr *LatencyResult) Append(latency *time.Duration, isErr bool) error {
	lr.mutex.Lock()
	defer lr.mutex.Unlock()
	lr.h.Update(int64(*latency))
	if isErr {
		lr.ErrCount++
	} else {
		lr.Count++
	}
	return nil
}

func (lr *LatencyResult) Print() error {
	lr.mutex.Lock()
	defer lr.mutex.Unlock()

	//calculate all metrics
	avg := time.Duration(lr.h.Mean())
	max := time.Duration(lr.h.Max())
	p50 := time.Duration(lr.h.Percentile(0.5))
	p90 := time.Duration(lr.h.Percentile(0.9))
	total := lr.Count + lr.ErrCount
	if total < 1 || lr.ExecSeconds == 0 {
		fmt.Printf("error: request Count or ExecSeconds = 0")
		return nil
	}
	fmt.Printf("exec duration: %fs\n", lr.ExecSeconds)
	fmt.Printf("total: %d, count: %d, error: %d, request/sec: %.2f ", total, lr.Count, lr.ErrCount, float64(total)/lr.ExecSeconds)
	fmt.Printf("avg: %v  max: %v  p50: %v  p90: %v \n", avg, max, p50, p90)
	return nil
}
