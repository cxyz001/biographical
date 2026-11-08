import java.util.*;
import java.util.concurrent.*;

/** 无测试框架依赖，失败直接抛 AssertionError；运行时不需要 -ea。 */
public final class OrderLabTest {
    static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    static void expect(Class<? extends Throwable> type, Runnable action) {
        try { action.run(); }
        catch (Throwable e) {
            if (type.isInstance(e)) return;
            throw new AssertionError("错误类型不符", e);
        }
        throw new AssertionError("预期失败但成功");
    }
    public static void main(String[] args) throws Exception {
        OrderLab.Store store = new OrderLab.Store();
        OrderLab.Input input = new OrderLab.Input(" book ", 2);
        var first = store.create("same", input);
        check(first.equals(store.create("same", input)), "重试应返回原订单");
        expect(IllegalStateException.class, () -> store.create("same", new OrderLab.Input("book", 3)));
        expect(IllegalArgumentException.class, () -> new OrderLab.Input("", 1));
        expect(IllegalArgumentException.class, () -> new OrderLab.Input("book", 0));
        expect(IllegalArgumentException.class, () -> store.create(" ", input));
        expect(NoSuchElementException.class, () -> store.transition(999, OrderLab.Status.PAID));
        expect(NullPointerException.class, () -> store.transition(first.id(), null));
        var paid = store.transition(first.id(), OrderLab.Status.PAID);
        check(paid.equals(store.transition(first.id(), OrderLab.Status.PAID)), "重复回调应幂等");
        expect(IllegalStateException.class, () -> store.transition(first.id(), OrderLab.Status.CANCELLED));
        check(store.create("same", input).status() == OrderLab.Status.PAID, "重放应返回同一订单当前状态");
        ExecutorService pool = Executors.newFixedThreadPool(8);
        try {
            List<Future<OrderLab.Order>> futures = new ArrayList<>();
            for (int i = 0; i < 100; i++) futures.add(pool.submit(() -> store.create("concurrent", input)));
            long id = futures.get(0).get(3, TimeUnit.SECONDS).id();
            for (var future : futures) check(future.get(3, TimeUnit.SECONDS).id() == id, "并发重复创建");
            check(store.size() == 2, "唯一订单数量错误");
        } finally { pool.shutdownNow(); }
        ThreadPoolExecutor bounded = new ThreadPoolExecutor(1, 1, 0, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(1), new ThreadPoolExecutor.AbortPolicy());
        CountDownLatch running = new CountDownLatch(1), release = new CountDownLatch(1);
        try {
            bounded.submit(() -> {
                running.countDown();
                try { release.await(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
            });
            check(running.await(3, TimeUnit.SECONDS), "任务未启动");
            bounded.submit(() -> {});
            expect(RejectedExecutionException.class, () -> bounded.submit(() -> {}));
        } finally {
            release.countDown();
            bounded.shutdownNow();
            check(bounded.awaitTermination(3, TimeUnit.SECONDS), "线程池未退出");
        }
        System.out.println("PASS：输入、幂等、状态迁移、100 次并发提交、队列拒绝与退出");
    }
}
