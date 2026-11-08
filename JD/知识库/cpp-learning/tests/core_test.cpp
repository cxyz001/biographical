#include "core.hpp"
#include <atomic>
#include <future>
#include <iostream>
#include <thread>

void check(bool condition) {
    if (!condition) throw std::runtime_error("check failed");
}
int main() {
    try {
        bool threw = false;
        try { BoundedQueue<int> bad(0); } catch (const std::invalid_argument&) { threw = true; }
        check(threw);
        BoundedQueue<int> q(1);
        check(q.try_push(7)); check(!q.try_push(8));
        q.close(); q.close();
        check(!q.try_push(9)); check(q.pop() == 7); check(!q.pop());

        BoundedQueue<int> empty(2);
        std::promise<void> started;
        auto waiting = std::async(std::launch::async, [&] { started.set_value(); return empty.pop(); });
        started.get_future().wait();
        empty.close(); check(!waiting.get());

        BoundedQueue<int> concurrent(32);
        std::atomic<int> count{0};
        std::atomic<long long> sum{0};
        std::vector<std::thread> consumers;
        for (int i=0; i<3; ++i) consumers.emplace_back([&] {
            while (auto value = concurrent.pop()) { ++count; sum.fetch_add(*value); }
        });
        std::vector<std::thread> producers;
        for (int p=0; p<2; ++p) producers.emplace_back([&,p] {
            for (int i=1; i<=1000; ++i) {
                int value = p*1000+i;
                while (!concurrent.try_push(value)) std::this_thread::yield();
            }
        });
        for (auto& t : producers) t.join();
        concurrent.close();
        for (auto& t : consumers) t.join();
        check(count == 2000); check(sum == 2001000);

        // Every possible two-chunk split, including split length header.
        auto bytes = encode("abc");
        auto second = encode(""); bytes.insert(bytes.end(), second.begin(), second.end());
        for (std::size_t split=0; split<=bytes.size(); ++split) {
            FrameDecoder d; std::vector<std::string> frames;
            auto emit = [&](std::string s) { frames.push_back(std::move(s)); };
            d.feed({bytes.begin(), bytes.begin()+split}, emit);
            d.feed({bytes.begin()+split, bytes.end()}, emit);
            check(frames == std::vector<std::string>({"abc", ""})); check(!d.incomplete());
        }
        FrameDecoder fragmented;
        int emitted = 0;
        for (auto b : encode(std::string(1024, 'x')))
            fragmented.feed({b}, [&](std::string s) { check(s.size()==1024); ++emitted; });
        check(emitted == 1);
        FrameDecoder partial; partial.feed({0,3,'a'}, [](std::string){}); check(partial.incomplete());
        FrameDecoder invalid;
        threw=false;
        try { invalid.feed({4,1}, [](std::string){}); } catch(const std::length_error&) { threw=true; }
        check(threw); threw=false;
        try { invalid.feed({}, [](std::string){}); } catch(const std::logic_error&) { threw=true; }
        check(threw); threw=false;
        try { encode(std::string(1025,'x')); } catch(const std::length_error&) { threw=true; }
        check(threw);
        std::cout << "PASS: queue boundaries, close/drain, wakeup, MPMC count/sum, frame splits, limits, truncation\n";
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
