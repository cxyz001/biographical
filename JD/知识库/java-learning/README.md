# Java 学习配套实验

教材：[Java 语言零基础到微服务实战](../03-Java语言零基础到微服务实战.md)。

## 运行

需要 JDK 17+，不需要 Maven、第三方依赖或数据库。在本目录的 PowerShell 中运行：

```powershell
$build = Join-Path $env:TEMP 'java-learning-classes'
javac -classpath . -encoding UTF-8 -d $build OrderLab.java OrderLabTest.java
if ($LASTEXITCODE -ne 0) { throw '编译失败' }
java -cp $build OrderLabTest
java -cp $build OrderLab
```

`OrderLabTest` 成功时打印 PASS，失败时抛 AssertionError 并以非零状态退出；不需要 `-ea`。`OrderLab` 显示同一幂等键的并发创建结果，最后唯一订单数应为 1。

中文显示不正常时，可先执行：

```powershell
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
```

## 代码怎样读

1. `Input` 紧凑构造器：规范化并验证输入。
2. `Order` 与 `Status`：不可变结果和最小状态机。
3. `Store.create`：同一临界区内检查幂等键并创建。
4. `Store.transition`：终态重复回调幂等，禁止非法迁移。
5. `main`：具名线程、有界队列、显式拒绝、Future 取错及关闭。
6. `OrderLabTest`：业务失败、并发提交与队列饱和验证。

测试中固定线程池只提交已知数量的 100 个任务，用于制造竞争；主程序演示有界队列。两者的任务输入规模与目的不同，不应把测试代码直接当作无上限生产任务入口。

## 验证范围

2026-10-23，Windows、JDK 17.0.14：本地编译及验收通过。检查输入拒绝、重复请求、同键不同参数、订单状态幂等、非法迁移、并发唯一订单、队列满拒绝和线程池退出。

这是单进程内存实验，没有 HTTP、持久化、真实支付、权限、多实例或设备接入；重启丢失数据。教材 V1～V6 和行业项目是后续开发练习，未声称已经完成 Spring 集成、数据库事务测试、容器部署、性能压测或设备联调。

## 来源

[sources.json](./sources.json) 记录实际读取的上游文件和下载文本哈希；[search-results.json](./search-results.json) 记录 GitHub 仓库检索结果。源码主分支可能变化，完整复现上游项目需选择固定 tag/commit，并使用其要求的工具链。
