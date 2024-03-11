package common

import (
	"fmt"
	"sort"
	"time"
)

type LantencyResult struct {
	Lantencys   []*time.Duration
	Count       int
	ErrCount    int
	ExecSeconds float64
}

func (lr *LantencyResult) Append(lantencyResult *LantencyResult) error {
	lr.Lantencys = append(lr.Lantencys, lantencyResult.Lantencys...)
	lr.Count += lantencyResult.Count
	lr.ErrCount += lantencyResult.ErrCount
	return nil
}

func (lr *LantencyResult) Print() error {
	var sum time.Duration

	//sort lantencys asc
	sort.Slice(lr.Lantencys, func(i, j int) bool {
		return *lr.Lantencys[i] < *lr.Lantencys[j]
	})

	for _, d := range lr.Lantencys {
		sum += *d
	}

	//calculate all metrics
	avg := sum / time.Duration(len(lr.Lantencys))
	max := lr.Lantencys[len(lr.Lantencys)-1]
	p50 := percentile(lr.Lantencys, 50)
	p90 := percentile(lr.Lantencys, 90)
	total := lr.Count + lr.ErrCount
	if total < 1 || lr.ExecSeconds == 0 {
		fmt.Printf("error: request Count or ExecSeconds = 0")
		return nil
	}
	fmt.Printf("total: %d, count: %d, error: %d, request/sec: %.2f ", total, lr.Count, lr.ErrCount, float64(total)/lr.ExecSeconds)
	fmt.Printf("avg: %v  max: %v  p50: %v  p90: %v \n", avg, max, p50, p90)
	return nil
}

func percentile(list []*time.Duration, p int) *time.Duration {

	if len(list) == 0 || p < 0 || p > 100 {
		d := time.Second * 0
		return &d
	}

	if p == 0 {
		return list[0]
	}

	if p == 100 {
		return list[len(list)-1]
	}
	// 计算百分位数的位置
	index := float64(p) / 100 * (float64(len(list)) - 1)
	// 如果位置是整数，返回列表中对应的值
	if index == float64(int64(index)) {
		return list[int(index)]
	}
	// 如果位置是小数，返回列表中两个相邻值的线性插值
	i := int(index)
	f := index - float64(i)
	d := time.Duration(float64(*list[i]) + f*float64(*list[i+1]-*list[i]))
	return &d
}
