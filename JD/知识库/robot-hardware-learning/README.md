# 机器人与硬件学习实验

教程：[机器人与硬件设计零基础到项目实战](../10-11-机器人与硬件设计零基础到项目实战.md)。

Python 3.9+，标准库，无需 ROS、仪器或开发板。从仓库根目录运行：

```bash
python JD/robot-hardware-learning/lab.py kinematics
python JD/robot-hardware-learning/lab.py energy
python JD/robot-hardware-learning/lab.py budget
python JD/robot-hardware-learning/lab.py audit
python -m unittest discover -s JD/robot-hardware-learning -p test_lab.py -v
```

预期：

- kinematics：左右轮约 2.5、5.5rad/s，仅理想无滑动转换。
- energy：1000Wh，输入 W/秒，梯形积分，非负功率。
- budget：输出2.66W，假定效率0.9，输入约2.956W、损耗约0.296W。
- audit：三条虚构低压数据分别 pass/review/fail。

`measurements.csv` 是虚构教学数据。审查采用测量区间整体落入限值才pass的保守示例；不是任何认证或实验室的统一规则。重复序列号拒绝处理，实际产线应引入显式重测编号与历史，不直接覆盖。

7 项测试覆盖运动方向/几何输入、积分单位/不等间隔采样、无效时间/数值、电源能量平衡、测量边界与CSV追溯。程序没有设备IO、控制器、物理仿真、硬件保护或完整产测系统；当前不模拟负功率、累计寄存器回绕或长缺样策略。

真实 ROS、总线、EDA、SPICE、充电软件及仪器实验的环境与验收见教程，尚未在本机执行。纯软件结果不能用作实物动作、线路选型、电气保护或认证依据。

另有两个待环境验证的实验：`trajectory_demo.py` 使用成熟 Ruckig 库生成单轴离线轨迹，需独立虚拟环境安装 ruckig 并记录版本；`rc.cir` 可由 ngspice 执行。具体命令见教程第11、19章。这两项不属于7项标准库测试的验证范围。

`research.py` 可重跑初次 GitHub 搜索和文件读取，`sources.json` 还记录了迁移/路径修正后的补充读取；重跑初次脚本会生成当时的新结果，不保留手动追加记录。开发项目需另外固定提交与依赖，正文哈希不是依赖锁文件。
