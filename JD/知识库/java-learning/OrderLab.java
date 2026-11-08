import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** JDK 17+，无外部依赖；仅演示单进程内存规则。 */
public final class OrderLab {
    public record Input(String sku, int quantity) {
        public Input {
            Objects.requireNonNull(sku, "sku");
            sku = sku.trim();
            if (sku.isEmpty() || sku.length() > 100 || quantity < 1 || quantity > 1000)
                throw new IllegalArgumentException("商品或数量无效");
        }
    }
    public enum Status { CREATED, PAID, CANCELLED }
    public record Order(long id, Input input, Status status) {}
    private record Entry(Input input, long id) {}
    public static final class Store {
        private final Map<String, Entry> keys = new HashMap<>();
        private final Map<Long, Order> orders = new HashMap<>();
        private long sequence;
        public synchronized Order create(String key, Input input) {
            Objects.requireNonNull(input, "input");
            if (key == null || key.isBlank() || key.length() > 128)
                throw new IllegalArgumentException("幂等键无效");
            Entry old = keys.get(key);
            if (old != null) {
                if (!old.input().equals(input)) throw new IllegalStateException("同键不同参数");
                return orders.get(old.id());
            }
            Order order = new Order(++sequence, input, Status.CREATED);
            orders.put(order.id(), order);
            keys.put(key, new Entry(input, order.id()));
            return order;
        }
        public synchronized Order transition(long id, Status target) {
            Objects.requireNonNull(target, "target");
            Order old = orders.get(id);
            if (old == null) throw new NoSuchElementException("订单不存在");
            if (old.status() == target) return old;
            if (old.status() != Status.CREATED || target == Status.CREATED)
                throw new IllegalStateException("不允许的状态迁移");
            Order next = new Order(id, old.input(), target);
            orders.put(id, next);
            return next;
        }
        public synchronized int size() { return orders.size(); }
    }
    public static void main(String[] args) throws Exception {
        Store store = new Store();
        AtomicInteger number = new AtomicInteger();
        ThreadPoolExecutor pool = new ThreadPoolExecutor(2, 4, 30, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(8),
            task -> new Thread(task, "order-lab-" + number.incrementAndGet()),
            new ThreadPoolExecutor.AbortPolicy());
        try {
            List<Future<Order>> futures = new ArrayList<>();
            for (int i = 0; i < 8; i++)
                futures.add(pool.submit(() -> store.create("retry-001", new Input("book", 2))));
            for (Future<Order> future : futures) System.out.println(future.get(2, TimeUnit.SECONDS));
            System.out.println("唯一订单数：" + store.size());
        } finally {
            pool.shutdown();
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) pool.shutdownNow();
        }
    }
}
