# 嵌入式 Linux 与边缘计算学习实验

教程：[从零到嵌入式 Linux 与边缘计算实战](../06-嵌入式Linux零基础到边缘计算实战.md)。

## 1. 无开发板实验：断网缓存与重试去重

依赖 Python 3.9+ 标准库；从仓库根目录运行，数据库写在指定练习目录。Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force build/edge-lab
python JD/embedded-learning/edge_lab.py --db build/edge-lab/local.db --capacity 3 collect --count 5
python JD/embedded-learning/edge_lab.py --db build/edge-lab/local.db status
python JD/embedded-learning/edge_lab.py --db build/edge-lab/local.db --remote build/edge-lab/remote.db flush --fail-after-receive
python JD/embedded-learning/edge_lab.py --db build/edge-lab/local.db --remote build/edge-lab/remote.db flush
python -m unittest discover -s JD/embedded-learning -p test_edge_lab.py -v
```

Linux 将第一条改为 `mkdir -p build/edge-lab`，其余命令按环境使用 `python3`。首次 collect 应接受 3 条、拒绝 2 条。注入失败的命令预期非零退出；下一次 flush 恢复后 pending 为 0，remote_unique 为 3。重复使用已有数据库会改变计数，请用新的练习目录复现首次运行。

发送顺序：本地事务保存 → 接收端事务保存且主键去重 → 本地删除已确认记录。失败点在“接收端已提交、本地未确认”之间，重新运行会重发，但接收端只计一次。每次采集有独立 session，避免重启后 sequence 从零开始发生碰撞。

7 项自动测试覆盖容量、重复与 session、校验、数据库重开、确认前失败重试、同 ID 内容冲突、独立进程失败后恢复。已在本机 Windows/Python 3.11 运行通过。

这个模型没有实际断开网络，不是 MQTT 实现。容量限制的是待发记录数，不是磁盘字节数；SQLite 删除数据可能只回收内部空闲页，不立即缩小文件。接收端去重表也需要保留策略。不能将进程异常测试称为断电、flash 或文件系统一致性测试。业务去重依赖唯一 ID 与去重记录仍在；重试必须沿用原始 payload。程序每次持久化后才返回 accepted，但断电可靠性还取决于 SQLite、OS、文件系统和存储设备。

## 2. Linux C 用户态实验

`read_lines.c` 演示 poll、超时、EINTR、短读、EOF 和有界行协议。它不是串口初始化代码，也不是驱动。需在 Linux/POSIX 环境编译；当前 Windows 主机未执行此部分。

```bash
mkdir -p build/edge-lab
cc -std=c11 -Wall -Wextra -Werror -O0 -g JD/embedded-learning/read_lines.c -o build/edge-lab/read_lines
printf 'temperature=23.5\nstatus=ok\n' | build/edge-lab/read_lines
printf 'unfinished' | build/edge-lab/read_lines
```

第一条管道输出两行且退出 0；第二条报告截断并退出 2。可继续测试 80/81 字节记录、慢输入和无换行 EOF。这里只检查流量边界，没有验证字段语义、编码或校验和。TCP、串口与普通文件的超时/EOF 语义还需分别适配。

## 3. Linux 服务模板

`edge-lab.service` 是 systemd oneshot 部署模板，前提是创建 edge 用户、安装 Python、把脚本部署到 /opt/edge-lab。它执行一次采集就退出，不是持续采集服务；不要误加 Restart=always。可配合 timer 周期触发。当前未在 systemd 上加载验证，也没有访问真实设备权限。

## 4. 资料核验

`search-results.json` 记录 GitHub 实际搜索结果；`sources.json` 记录实际下载文件、分支、日期、文本长度与 SHA-256。摘要是文本内容摘要，不是 commit。`research.py` 和 `read_sources.py` 是检索辅助脚本；联网重新运行会刷新记录并生成临时 research.json，其中含上游文件全文，不建议提交该临时文件。

扩展路径：把模拟采样替换为 Linux C/串口采集；把 Receiver 替换为带业务确认的网络 API；加入磁盘字节上限与配额；最后在开发板执行异常退出、网络故障和断电验证。设备驱动、OTA、RTOS 与 NPU 内容见教程，不在便携实验里冒充已实现。
