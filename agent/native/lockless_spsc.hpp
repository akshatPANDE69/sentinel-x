#ifndef SENTINEL_LOCKLESS_SPSC_HPP
#define SENTINEL_LOCKLESS_SPSC_HPP

#include <atomic>
#include <cstddef>
#include <new>
#include <type_traits>
#include <utility>
#include <vector>

constexpr size_t CACHE_LINE_SIZE = 64;

/**
 * Cache-Aligned Lockless Single-Producer Single-Consumer (SPSC) Ring Buffer
 * 
 * Guarantees:
 * 1. Zero mutexes / Zero syscalls / Zero thread-blocking locks.
 * 2. Cache-line alignment (alignas(64)) preventing false sharing between Producer (Kernel) and Consumer (User).
 * 3. Acquire-Release memory order semantics ensuring sequential consistency of telemetry records.
 */
template <typename T, size_t Capacity = 65536>
class LocklessSPSCQueue {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2 for fast bitmask indexing");
    static constexpr size_t BufferMask = Capacity - 1;

public:
    LocklessSPSCQueue() : head_(0), tail_(0) {
        buffer_ = static_cast<T*>(::operator new[](sizeof(T) * Capacity, std::align_val_t{CACHE_LINE_SIZE}));
    }

    ~LocklessSPSCQueue() {
        T dummy;
        while (pop(dummy));
        ::operator delete[](buffer_, std::align_val_t{CACHE_LINE_SIZE});
    }

    // Producer (Ring 0 / Kernel Thread)
    template <typename... Args>
    bool emplace(Args&&... args) {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_.load(std::memory_order_acquire);

        if ((current_head - current_tail) >= Capacity) {
            return false; // Queue full
        }

        new (&buffer_[current_head & BufferMask]) T(std::forward<Args>(args)...);
        head_.store(current_head + 1, std::memory_order_release);
        return true;
    }

    bool push(const T& item) {
        return emplace(item);
    }

    // Consumer (Ring 3 / User-Mode Security Agent)
    bool pop(T& val) {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        const size_t current_head = head_.load(std::memory_order_acquire);

        if (current_tail == current_head) {
            return false; // Queue empty
        }

        val = std::move(buffer_[current_tail & BufferMask]);
        buffer_[current_tail & BufferMask].~T();
        tail_.store(current_tail + 1, std::memory_order_release);
        return true;
    }

    size_t size() const {
        const size_t h = head_.load(std::memory_order_relaxed);
        const size_t t = tail_.load(std::memory_order_relaxed);
        return (h >= t) ? (h - t) : 0;
    }

    bool empty() const {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

private:
    T* buffer_;

    // Separate Head and Tail onto independent 64-byte cache lines to eliminate False Sharing
    alignas(CACHE_LINE_SIZE) std::atomic<size_t> head_;
    alignas(CACHE_LINE_SIZE) std::atomic<size_t> tail_;
};

#endif // SENTINEL_LOCKLESS_SPSC_HPP
