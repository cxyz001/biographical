#include "core.hpp"
#include <iostream>
#include <thread>

int main() {
    BoundedQueue<std::string> queue(4);
    std::thread worker([&queue] {
        while (auto item = queue.pop()) std::cout << "processed: " << *item << '\n';
    });
    // Join on every path, including decoder or allocation exceptions.
    try {
        FrameDecoder decoder;
        auto packet = encode("temperature=23.5");
        decoder.feed({packet.begin(), packet.begin() + 1}, [&](std::string x) {
            if (!queue.try_push(std::move(x))) throw std::runtime_error("queue rejected frame");
        });
        decoder.feed({packet.begin() + 1, packet.end()}, [&](std::string x) {
            if (!queue.try_push(std::move(x))) throw std::runtime_error("queue rejected frame");
        });
        if (decoder.incomplete()) throw std::runtime_error("truncated frame");
    } catch (const std::exception& e) {
        queue.close();
        worker.join();
        std::cerr << e.what() << '\n';
        return 1;
    }
    queue.close();
    worker.join();
}
