# 数据开发工程师

- **公司**：某大型互联网公司
- **薪资**：20-30K
- **城市**：深圳龙华区龙华数字智造中心6号楼9层

- **标签**：Java, 要求数据开发经验, 开, Doris/Druid, ETL开发经验, 开, PostgreSQL, 数据建模经验
- **职位链接**：https://www.zhipin.com/job_detail/dd3bf46870217e4a0nNz3tu0EVVQ.html?securityId=oyOcClwxYR9l2-81DtHxPSXhLk2KsEMXrj4LNF0fdiqjn7X8cEhLL-hNiqvHkJS_LBV6JL7ahB5vWaf9jQ0RQ5s8FhmXFNdRFLN9exZ8wd9J9wT3Hq5O&ka=personal_interest_job_dd3bf46870217e4a0nNz3tu0EVVQ
- **职位 ID**：dd3bf46870217e4a0nNz3tu0EVVQ

## 职位描述

团队介绍：
湖仓一体架构：Apache Iceberg（REST Catalog + MinIO）承载 ODS 湖表，Apache Doris 经 REST Catalog 直连做计算与 DWD/ADS 加速，dbt 承载全部 SQL 转换，Dagster 做调度编排；
数据源：领星 ERP（采购/库存/订单/财务等业务域）、飞书项目、文件上传等 10+ 来源，⾃研声明式数据源接⼊框架（spec DSL），新源接⼊以配置为主；
出口：FastAPI 数据网关 + Superset 看板 + ChatBI 自然语⾔取数；
治理：OpenMetadata 元数据与血缘、列级数据字典贯通（dbt → manifest → 调度层）、数据质量与新鲜度告警直达飞书机器人；
工程文化：CI 全绿、模型带测试、决策写 ADR、文档齐全。
目前平台处于起步阶段，由小团队维护，我们希望找到一位能独立扛起湖仓架构演进与日常建设的工程师，把它从「能用」带到「规模化的好用」。资源有限，目前单机，后续规模化后可转分布式。
岗位职责
1、湖仓架构演进：ODS / DWD / ADS 分层架构的持续设计——Iceberg 表设计与生命周期、Doris 物化与加速策略、查询性能优化、容量规划。按「未来的数据规模」设计，不以当前规模为上限。
2、数据集成建设：领星 ERP、飞书等 API 采集管道开发与维护——增量同步、分页限流、幂等写入、断点续传、上下游对账；参与声明式数据源框架迭代。
3、建模与转换：dbt 维度/事实建模与增量 MERGE，编写模型测试，维护列级元数据与口径定义。
4、调度与稳定性：Dagster schedules / sensors / freshness 策略，质量与新鲜度告警，线上数据问题排查、归因与恢复。
5、数据治理：血缘与元数据链路（dbt manifest → OpenMetadata）日常运转，指标口径统一，数据字典维护。
6、业务支持：响应取数需求，支撑 Superset 与 ChatBI 场景，把重复取数沉淀为模型。
7、参与技术决策并沉淀 ADR，保持测试与 CI 质量。
任职要求（必备）
1、3 年以上数据研发经验，完整负责过至少一个跑在生产上的数据平台 / 数仓项目；
2、以下技术至少熟悉三项，且对整体链路有完整认知：dbt、Dagster（或 Airflow）、Iceberg（或 Delta/Hudi）、Doris（或StarRocks/ClickHouse）、对象存储；
3、SQL 建模能力强（分层、缓慢变化维、增量 MERGE、幂等），Python 能写带测试的生产代码；
4、有 API 数据集成实战：鉴权、分页、限流、增量游标、重试、对账，认同「数据不对齐比数据晚到更严重」；
5、血缘、元数据、数据质量、口径管理；
6、能独立在 Linux 环境部署排障；
7、方案讲得清楚，事后写得下来。
加分项
跨境电商 / ERP 经验（领星、聚水潭、旺店通等），懂采购、库存、订单、财务链路；
飞书开放平台集成（机器人、审批、Meegle OpenAPI）；
OpenMetadata / DataHub 等元数据平台实战；
ChatBI / LLM 数据应用（语义层、Text2SQL）；
Trino / Spark / Flink，或湖仓选型、迁移、升级经历；
对「单机湖仓 → 多机 / 云原生」演进有实际思考；
开源贡献、技术博客。
