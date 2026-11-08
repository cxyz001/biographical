package main

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func request(h http.Handler, key, body string) *httptest.ResponseRecorder {
	r := httptest.NewRequest("POST", "/orders", strings.NewReader(body))
	r.Header.Set("Idempotency-Key", key)
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	return w
}

func TestCreateReplayConflictAndGet(t *testing.T) {
	h := NewHandler(NewStore())
	body := `{"sku":"book","quantity":2}`
	first := request(h, "k1", body)
	if first.Code != 201 {
		t.Fatal(first.Code, first.Body.String())
	}
	replay := request(h, "k1", body)
	if replay.Code != 200 || replay.Body.String() != first.Body.String() {
		t.Fatal("重试未返回同一订单")
	}
	if w := request(h, "k1", `{"sku":"book","quantity":3}`); w.Code != 409 {
		t.Fatal(w.Code)
	}
	var order Order
	if err := json.Unmarshal(first.Body.Bytes(), &order); err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	h.ServeHTTP(w, httptest.NewRequest("GET", "/orders/"+order.ID, nil))
	if w.Code != 200 {
		t.Fatal(w.Code)
	}
}

func TestInvalidInput(t *testing.T) {
	h := NewHandler(NewStore())
	for _, body := range []string{`{}`, `{"sku":"x","quantity":0}`, `{"sku":"x","quantity":1,"admin":true}`, `{"sku":"x","quantity":1} {}`, strings.Repeat("x", 5000)} {
		if w := request(h, "bad", body); w.Code != 400 {
			t.Fatalf("收到 %d", w.Code)
		}
	}
	if w := request(h, "", `{"sku":"x","quantity":1}`); w.Code != 400 {
		t.Fatal(w.Code)
	}
}

func TestConcurrentIdempotency(t *testing.T) {
	s := NewStore()
	var wg sync.WaitGroup
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if _, _, err := s.Create("same", createInput{"x", 1}); err != nil {
				t.Error(err)
			}
		}()
	}
	wg.Wait()
	if len(s.orders) != 1 {
		t.Fatal(len(s.orders))
	}
}

func TestParallelBoundAndOrder(t *testing.T) {
	var active, max atomic.Int32
	fetch := func(ctx context.Context, id string) (string, error) {
		n := active.Add(1)
		defer active.Add(-1)
		for old := max.Load(); n > old; old = max.Load() {
			if max.CompareAndSwap(old, n) {
				break
			}
		}
		select {
		case <-ctx.Done():
			return "", ctx.Err()
		case <-time.After(time.Millisecond):
			return id, nil
		}
	}
	result, err := Parallel(context.Background(), []string{"a", "b", "c", "d"}, 2, fetch)
	if err != nil || strings.Join(result, "") != "abcd" || max.Load() > 2 {
		t.Fatal(result, err, max.Load())
	}
}

func TestParallelCancellationAndError(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	_, err := Parallel(ctx, []string{"a"}, 1, func(context.Context, string) (string, error) { return "", nil })
	if !errors.Is(err, context.Canceled) {
		t.Fatal(err)
	}
	want := errors.New("下游失败")
	_, err = Parallel(context.Background(), []string{"a", "b"}, 1, func(context.Context, string) (string, error) { return "", want })
	if !errors.Is(err, want) {
		t.Fatal(err)
	}
	if _, err := Parallel(context.Background(), nil, 0, nil); err == nil {
		t.Fatal("缺少参数检查")
	}
}

func BenchmarkStoreGet(b *testing.B) {
	s := NewStore()
	o, _, _ := s.Create("bench", createInput{"x", 1})
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		s.Get(o.ID)
	}
}
