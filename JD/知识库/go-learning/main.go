package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"
)

func main() {
	server := &http.Server{Addr: "127.0.0.1:8080", Handler: NewHandler(NewStore()),
		ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 10 * time.Second,
		WriteTimeout: 10 * time.Second, IdleTimeout: 60 * time.Second}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	done := make(chan error, 1)
	go func() { done <- server.ListenAndServe() }()
	log.Print("教学订单服务：http://127.0.0.1:8080；数据仅保存在内存")
	select {
	case err := <-done:
		if !errors.Is(err, http.ErrServerClosed) {
			log.Fatal(err)
		}
	case <-ctx.Done():
		shutdown, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := server.Shutdown(shutdown); err != nil {
			log.Printf("优雅退出失败：%v", err)
			_ = server.Close()
		}
		if err := <-done; !errors.Is(err, http.ErrServerClosed) {
			log.Printf("监听结束：%v", err)
		}
	}
}
