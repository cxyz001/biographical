// 教学服务：标准库 HTTP、并发安全存储、幂等创建和请求级取消。
package main

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"strings"
	"sync"
)

type Order struct {
	ID       string `json:"id"`
	SKU      string `json:"sku"`
	Quantity int    `json:"quantity"`
}

type entry struct {
	order Order
	input createInput
}
type createInput struct {
	SKU      string `json:"sku"`
	Quantity int    `json:"quantity"`
}
type Store struct {
	mu     sync.Mutex
	orders map[string]Order
	keys   map[string]entry
	next   int
}

func NewStore() *Store { return &Store{orders: make(map[string]Order), keys: make(map[string]entry)} }

var ErrConflict = errors.New("幂等键已用于不同请求")

func (s *Store) Create(key string, in createInput) (Order, bool, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if old, ok := s.keys[key]; ok {
		if old.input != in {
			return Order{}, false, ErrConflict
		}
		return old.order, false, nil
	}
	s.next++
	o := Order{ID: orderID(s.next), SKU: in.SKU, Quantity: in.Quantity}
	s.orders[o.ID] = o
	s.keys[key] = entry{order: o, input: in}
	return o, true, nil
}

func (s *Store) Get(id string) (Order, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	o, ok := s.orders[id]
	return o, ok
}

// 教学用整数转换；业务项目可以直接使用 strconv.Itoa 或可信 ID 生成器。
func orderID(n int) string {
	if n == 0 {
		return "0"
	}
	var b [20]byte
	i := len(b)
	for n > 0 {
		i--
		b[i] = byte('0' + n%10)
		n /= 10
	}
	return string(b[i:])
}

func respond(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}

func NewHandler(store *Store) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		respond(w, http.StatusOK, map[string]string{"status": "ok"})
	})
	mux.HandleFunc("POST /orders", func(w http.ResponseWriter, r *http.Request) {
		key := strings.TrimSpace(r.Header.Get("Idempotency-Key"))
		if len(key) == 0 || len(key) > 128 {
			http.Error(w, "需要长度 1~128 的幂等键", 400)
			return
		}
		r.Body = http.MaxBytesReader(w, r.Body, 4096)
		defer r.Body.Close()
		decoder := json.NewDecoder(r.Body)
		decoder.DisallowUnknownFields()
		var in createInput
		if err := decoder.Decode(&in); err != nil {
			http.Error(w, "无效 JSON 或请求体过大", 400)
			return
		}
		var extra any
		if err := decoder.Decode(&extra); err != io.EOF {
			http.Error(w, "只允许一个 JSON 对象", 400)
			return
		}
		in.SKU = strings.TrimSpace(in.SKU)
		if in.SKU == "" || len(in.SKU) > 100 || in.Quantity < 1 || in.Quantity > 1000 {
			http.Error(w, "商品或数量无效", 400)
			return
		}
		order, created, err := store.Create(key, in)
		if errors.Is(err, ErrConflict) {
			http.Error(w, err.Error(), 409)
			return
		}
		status := http.StatusOK
		if created {
			status = http.StatusCreated
		}
		respond(w, status, order)
	})
	mux.HandleFunc("GET /orders/{id}", func(w http.ResponseWriter, r *http.Request) {
		order, ok := store.Get(r.PathValue("id"))
		if !ok {
			http.NotFound(w, r)
			return
		}
		respond(w, http.StatusOK, order)
	})
	return mux
}

// Parallel 提交有界的一组独立任务；结果保留输入顺序。任务必须响应 ctx。
func Parallel(ctx context.Context, ids []string, limit int, fetch func(context.Context, string) (string, error)) ([]string, error) {
	if limit < 1 || len(ids) > 100 {
		return nil, errors.New("并发必须大于零，批量最多 100 项")
	}
	ctx, cancel := context.WithCancel(ctx)
	defer cancel()
	results := make([]string, len(ids))
	sem := make(chan struct{}, limit)
	var wg sync.WaitGroup
	var once sync.Once
	var first error
	setError := func(err error) { once.Do(func() { first = err; cancel() }) }
submit:
	for i, id := range ids {
		select {
		case sem <- struct{}{}:
		case <-ctx.Done():
			break submit
		}
		wg.Add(1)
		go func(i int, id string) {
			defer wg.Done()
			defer func() { <-sem }()
			if err := ctx.Err(); err != nil {
				setError(err)
				return
			}
			value, err := fetch(ctx, id)
			if err != nil {
				setError(err)
				return
			}
			results[i] = value
		}(i, id)
	}
	wg.Wait()
	if first != nil {
		return nil, first
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	return results, nil
}
