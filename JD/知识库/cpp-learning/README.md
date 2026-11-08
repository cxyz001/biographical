# C++ 学习实验

配套教程：[C++ 语言零基础到系统软件实战](../05-C++语言零基础到系统软件实战.md)。语言基线 C++17，仅依赖标准库和线程支持。

## 内容

- `include/core.hpp`：有界、可关闭、关闭后排空的线程安全队列；单线程增量拆帧器。
- `src/main.cpp`：模拟设备字节输入，拆帧后交给后台线程。
- `tests/core_test.cpp`：边界、关闭、并发计数、分片与长度校验。
- `sources.json`、`search-results.json`：实际 GitHub 阅读和搜索记录。
- `research.py`、`finish_research.py`：资料检索辅助脚本，不参与 C++ 构建，联网重跑会更新记录。

## Windows

从仓库根目录，在安装 VS 2022 C++ 工作负载、Windows SDK、CMake 后：

```powershell
cmake -S JD/cpp-learning -B build/cpp-learning -G "Visual Studio 17 2022" -A x64
cmake --build build/cpp-learning --config Debug
ctest --test-dir build/cpp-learning -C Debug --output-on-failure
./build/cpp-learning/Debug/telemetry_demo.exe
```

## Linux

```bash
cmake -S JD/cpp-learning -B build/cpp-learning -DCMAKE_BUILD_TYPE=Debug
cmake --build build/cpp-learning -j
ctest --test-dir build/cpp-learning --output-on-failure
./build/cpp-learning/telemetry_demo
```

期望输出：`processed: temperature=23.5`。测试失败返回非零；CTest 限时 20 秒防止生命周期错误永久挂起。

## 接口约定

队列容量必须大于零；满或关闭时 try_push 返回 false，不阻塞等待空间；close 可重复调用，随后 pop 排空已有元素再返回 nullopt。队列销毁前必须关闭并等待所有使用线程结束。模板用于课程中的 int/string；没有承诺对任意抛异常的元素移动操作提供相同异常保证。

帧为 2 字节大端长度 + payload，允许 0～1024 字节。拆帧器单线程使用，回调同步执行且不可重入；非法长度后实例失效，应结束该连接。incomplete 用于 EOF 时发现截断。输入缓冲和回调的资源开销由调用方管理。

本次验证：Windows x64、MSVC 19.43，Debug 编译、1 个 CTest 测试入口通过，demo 输出正确。测试入口内覆盖多项契约，不能据此声称已证明所有并发调度正确。未验证 Linux/ARM、Sanitizer、真实 socket、硬件与媒体依赖。实验不具备生产服务所需的超时、持久化、指标、进程信号和完整异常恢复。
