# 音视频学习配套实验

主教程：[音视频零基础到流媒体平台实战](../07-音视频零基础到流媒体平台实战.md)。

## 运行

Python 3.9+，仅使用标准库。从仓库根目录执行：

```powershell
New-Item -ItemType Directory -Force build/media-lab
python JD/media-learning/media_lab.py tone build/media-lab/tone.wav
python JD/media-learning/media_lab.py inspect build/media-lab/tone.wav
python JD/media-learning/media_lab.py timeline
python JD/media-learning/media_lab.py queue
python -m unittest discover -s JD/media-learning -p test_media_lab.py -v
```

Linux 首条替换为 `mkdir -p build/media-lab`，其余按环境使用 python3。tone 会覆盖指定输出文件，请使用专用练习路径。

预期结果：

- tone/inspect：16kHz、单声道、16bit、2 秒、32000 帧、64000 字节 PCM。
- timeline：90000 个 1/90000 秒刻度对应 1000 个毫秒刻度；1024/48000 秒为 8/375 秒。
- queue：消费 `[1,5,9]`，丢弃 `[0,2,3,4,6,7,8]`，剩余 `[10,11]`，峰值容量 3。

5 项测试覆盖 WAV 元数据与实际样本长度、非法输入与混叠频率、负时间戳与分数刻度、慢消费者丢弃守恒、快消费者及容量约束。

## 范围

这是 PCM 格式与调度模型实验，没有真实音视频采集、网络协议或模型推理。queue 只模拟已解码 AI 图像，不允许把策略直接用于任意 H.264/H.265 压缩包。rescale_exact 返回有理数，不处理 FFmpeg AV_NOPTS_VALUE、整数舍入或溢出。tone 的纯音不是 ASR 测试语料。

FFmpeg、媒体服务、WebRTC、设备和语音模型的操作前提见主教程。当前主机未发现 ffmpeg/ffprobe，因此未执行那些实验。

## 资料追溯

`search-results.json` 保存 GitHub 仓库搜索结果；`sources.json` 保存读取路径、日期、正文 SHA256 或实际失败原因。`research.py` 可重新检索并读取正文，依赖 GitHub 网络可达性与 API 速率限制。正文属于上游项目，不在此复制整份源码；学习代码为本目录独立编写的教学模型。
