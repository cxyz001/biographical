# Python 学习配套实验

教材：[Python 语言零基础到工程与算法实战](../04-Python语言零基础到工程与算法实战.md)。

需要 Python 3.11+，只依赖标准库。在本目录执行：

```powershell
python -B -m unittest -v
python -B document_lab.py README.md --top 5
python -B document_lab.py --help
```

如果希望隔离环境，可按教材第 2 章创建虚拟环境。中文显示不正常时，可设置当前终端与 Python 输出编码：

```powershell
$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
```

## 代码阅读顺序

1. `Report`：数据类、结果结构、浅层冻结。
2. `analyze`：有限文件读取、UTF-8 解码、计数、确定性排序、内容哈希。
3. `main`：参数解析、错误提示、JSON 输出和退出码。
4. `bounded_map`：Semaphore、TaskGroup、总预算与保序结果。
5. 测试：先检查业务结果，再看超时和失败怎样清理任务。

词频规则是英文词/数字串与中文单字，不是中文分词、AI 摘要或语义分析。输入只支持 UTF-8 文本（含 BOM），最多 1,000,000 字节；不支持 PDF、Office、OCR、压缩包。工具不上传文档，也不调用模型。

`bounded_map` 是独立的异步学习函数，未连接 CLI 或网络服务。输入最多 100 项，并发 1～100；fetch 需真正异步并响应取消。大规模输入需另行设计有限队列/worker，不能无上限复制这个小批量模式。

## 验证记录

2026-10-23，Windows、Python 3.11.9：5 项 unittest 测试通过，覆盖文本结果与哈希、重复运行一致、输入拒绝、并发上限与顺序、兄弟任务失败取消、超时清理和参数上限。

教材中的 FastAPI、SQLAlchemy、Celery、模型、打包、容器及行业项目为后续实现任务，本次未完成这些第三方系统的安装、集成、性能压测或生产部署。标准库测试通过不代表这些系统已经验证。

## 资料记录

- [检索记录](./search-results.json)：GitHub 搜索结果和请求失败情况。
- [来源记录](./sources.json)：实际读取文件及下载文本 SHA-256；不是 commit，分支链接会变化。

文档与代码是学习整理，不包含上游仓库全文副本。
