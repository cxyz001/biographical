# Java 基础软件研发（CDC / 数据同步引擎）

- **公司**：京东集团
- **薪资**：35-55K·14薪
- **城市**：深圳南山区万海大厦B座502A 点击查看地图
- **标签**：Java, MySQL, Redis, MongoDB, Oracle
- **职位链接**：https://www.zhipin.com/job_detail/f683c4df7d29bcc30nN60tS9E1tQ.html?securityId=va2v-wmW6eirb-51vOSp1CxhDPzaKL2lU1RCyOPFD6xihljonS-03rvTq8LjPbqS6kLt3xNscv0f0pRAVWrzpxL-_jjb07UTaw4V59JHXQS3hiVO-CgIML0~&ka=personal_interest_job_f683c4df7d29bcc30nN60tS9E1tQ
- **职位 ID**：f683c4df7d29bcc30nN60tS9E1tQ

## 职位描述

Tapdata 做企业级数据集成和实时同步产品。这个岗位写的是同步引擎和连接器，不是数仓、数据治理或数据中台。
适合你，如果做过其中至少一件：
• 解析或实现过 MySQL binlog / PostgreSQL WAL / MongoDB oplog / Oracle 日志复制
• 开发或改过 Canal、Debezium、Flink CDC、Kafka Connect、自研 CDC
• 写过 Source / Sink 连接器，处理过类型映射、幂等写⼊、Schema 变更
⼯作职责
1. 参与核⼼同步引擎研发：任务 Runtime、状态、Checkpoint、反压、故障恢复、Exactly-Once。
2. 实现或加固 CDC 采集：快照切增量、位点（GTID / LSN 等）、DDL、大事务、⽆主键、断点续传。
3. 开发 Source / Sink 连接器，处理异构库差异、类型映射、幂等写入和 Schema 变更。
4. 解决高吞吐、低延迟、长时间运行下的内存、线程、积压和稳定性问题。
5. 排查生产问题：读日志、做最小复现、验证修复，并把故障变成可回归的测试。
任职要求
1. 本科及以上，5 年以上 Java 开发，近 3 年仍在写核心代码。
2. 熟悉 JVM、并发、网络 IO、内存和常见性能问题，能独立排查线上故障。
3. 具备以下至少一类开发经验（使用工具搭链路不算）：
   • CDC / 日志复制：Debezium、Canal、Maxwell、Kafka Connect、自研 binlog/WAL 解析、数据库复制组件
   • 连接器：Source / Sink 插件，或对 Flink CDC Connector 做过源码级改动
   • 流引擎 Runtime：Flink Operator / Runtime、Kafka Streams 或自研引擎框架层，而不是 SQL 作业
4. 深入理解至少一种数据库的复制机制（MySQL binlog、PostgreSQL logical decoding，或 Oracle / SQL Server / MongoDB 同等经验）。
5. 能讲清 at-least-once / exactly-once，以及 checkpoint 与下游写入如何对齐。
加分
• 数据库厂商、数据同步 / CDC 产品、中间件或云数据库研发经历
• Oracle、SQL Server、DB2、MongoDB 等异构 CDC
• 开源 CDC / 连接器贡献，或能讲清一次真实的丢数、重复、位点跳跃问题
• 英语可读设计文档、能参与技术讨论
