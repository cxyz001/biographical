#pragma once
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Reject-new policy: the caller decides whether to retry, persist, or discard.
template<class T> class BoundedQueue {
    std::mutex mutex_;
    std::condition_variable ready_;
    std::deque<T> queue_;
    const std::size_t capacity_;
    bool closed_ = false;
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {
        if (!capacity) throw std::invalid_argument("capacity must be positive");
    }
    bool try_push(T value) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (closed_ || queue_.size() == capacity_) return false;
            queue_.push_back(std::move(value));
        }
        ready_.notify_one();
        return true;
    }
    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        ready_.wait(lock, [this] { return closed_ || !queue_.empty(); });
        if (queue_.empty()) return std::nullopt;
        T value = std::move(queue_.front());
        queue_.pop_front();
        return value;
    }
    void close() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            closed_ = true;
        }
        ready_.notify_all();
    }
};

// Wire format: two-byte big-endian length, then 0..1024 payload bytes.
// Single-thread-owned decoder. An invalid header poisons this connection.
class FrameDecoder {
    std::vector<std::uint8_t> pending_;
    std::size_t expected_ = 0;
    bool header_ready_ = false;
    bool failed_ = false;
public:
    static constexpr std::size_t max_payload = 1024;
    template<class Emit> void feed(const std::vector<std::uint8_t>& bytes, Emit emit) {
        if (failed_) throw std::logic_error("decoder failed; replace connection");
        for (auto byte : bytes) {
            pending_.push_back(byte);
            if (!header_ready_ && pending_.size() == 2) {
                expected_ = (std::size_t(pending_[0]) << 8) | pending_[1];
                pending_.clear();
                if (expected_ > max_payload) {
                    failed_ = true;
                    throw std::length_error("payload too large");
                }
                header_ready_ = true;
            }
            if (header_ready_ && pending_.size() == expected_) {
                std::string payload(pending_.begin(), pending_.end());
                pending_.clear();
                header_ready_ = false;
                emit(std::move(payload));
            }
        }
    }
    bool incomplete() const { return header_ready_ || !pending_.empty(); }
};

inline std::vector<std::uint8_t> encode(const std::string& payload) {
    if (payload.size() > FrameDecoder::max_payload)
        throw std::length_error("payload too large");
    std::vector<std::uint8_t> out;
    out.reserve(payload.size() + 2);
    out.push_back(static_cast<std::uint8_t>(payload.size() >> 8));
    out.push_back(static_cast<std::uint8_t>(payload.size() & 0xff));
    out.insert(out.end(), payload.begin(), payload.end());
    return out;
}
