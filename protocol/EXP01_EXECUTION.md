# 实验一：冻结的首轮运行协议

日期：2026-11-03。授权范围：用户要求设置环境并完成实验一。先执行四个网络各一次，不等同于完成三次独立重复。

## 环境

- Windows Python 3.11.4：仅作为实验控制器与接口审计网关，研究模型无执行权限。
- 已安装的 DeepSeek Harness CLI：0.2.1-rc.5。
- 原实验提交：4d09ba6d6a7e891dd8063974dfe81b3d78e3494f。
- 用于查阅接口的 Harness 源码提交：ce7073d51254c26cd63b22a60835b8f948deb447；不冒称与已安装二进制完全相同。
- `configs/dsh-headless-base.yml` 保存已安装客户端的默认配置快照；运行器生成禁用无关插件的覆盖配置。
- 每个任务独立 DSH_HOME 和工作目录，不修改用户桌面客户端默认配置。

## 模型实际输入

系统指令：`Answer the user's request.`

用户消息：各游戏原始 prompt.txt 全文；不添加候选游戏、真实标签、旧答案或研究者解释。源文件字节哈希与换行规范化后文本哈希分别记录。

模型 `deepseek-flash`，thinking enabled，High；最大输出 32,768 tokens。无工具、无自动续写、无模型请求重试；遇截断或错误停下并保留记录。

使用已安装 Harness 自带 Anthropic Messages 传输，High 在请求中表现为 `output_config.effort=high`。没有额外 top_p 参数，保留服务默认采样。这与早期计划的 top_p 候选值不同，明确记录而不伪装为已设置。

## 出站审计

客户端将请求交给仅监听 127.0.0.1 的本地网关。网关在转发前检查：

- 正确模型、High、thinking 与输出上限；
- 系统提示完全一致；
- 恰好一条完整用户消息；
- 没有工具；
- 每个任务仅一次请求；
- 请求体小于 200,000 字节。

认证密钥仅由控制器读取并用于官方 `https://api.deepseek.com/anthropic/v1/messages`；客户端得到的是本地网关占位凭据。网关不保存认证头。

预算：本批上限 1 美元，四次请求、每次最多 32,768 输出 tokens，无重试。按核验的官方峰时输入/输出价格、输入字节规模作保守规划，四次总量估计低于该上限；实际费用依据 usage 和服务账单报告，不把预估当作账单。参考：https://api-docs.deepseek.com/quick_start/pricing/ 。

## 轨迹

`runs/exp01/<batch>/<network-id>/` 保存 request.json、原始 response.sse、reasoning.md、answer.md、events.jsonl、stderr.log、audit.json、source.json 和 result.json。

重要：Harness 的 JSON 事件投影存在字符串长度限制，所以原始 SSE 是推理保存的主来源；不能仅依赖 events.jsonl。

## 评分

只对 Game 行分类，Frogger 按原研究规则计为 Freeway。歧义或缺少 Game 行单列，不根据思维链替模型选答案。自动匹配后人工复核原文。置信度只报告模型自述，不作为正确性的证据。

## 执行

无费用配置测试：`python src/exp01.py`。

正式四任务：`python src/exp01.py --live`。

密钥从进程环境或 Windows 用户环境变量 DEEPSEEK_API_KEY 读取。未配置时退出，不发送请求。不要把密钥写进代码、聊天或 Git。

## 已完成验证

2026-11-03 的四个离线模拟任务均通过实际请求审计，均只出现一次请求，原始推理流与答案文件正常生成。模拟结果明确标为 live=false，不是 Flash 能力结果。

正式模型运行当前待密钥配置；以 live 批次记录和最终报告为准。
