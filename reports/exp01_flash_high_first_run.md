# 实验一首轮结果：Flash + High

日期：2026-11-03。批次：`live_20261103T053114Z`。研究者模型服务返回 ID：deepseek-flash。

## 结果

四个原网络各一次独立调用。三题正常结束且识别正确，一题因输出达到上限而没有最终答案。

| 真值 | 最终 Game 行 | 自报置信度 | 停止原因 | 输出 tokens | 秒 |
|---|---|---|---|---:|---:|
| breakout | Breakout—a simplified/10×10-grid version of Atari Breakout. | 96.0% | end_turn | 30,785 | 179.2 |
| pong | Pong, specifically a Pong-like tennis game on a 10×10 grid with an 8×8 playable interior. | 94.0% | end_turn | 23,508 | 120.6 |
| pacman | Pac-Man (a small grid Pac-Man-style maze game; most likely the Pac-Man environment rather than Ms. Pac-Man). | 93.0% | end_turn | 29,337 | 148.1 |
| freeway | 无最终 Game 行 | — | max_tokens | 32,768 | 175.7 |

全部启动任务的有效正确回答率为 **3/4（75%）**，正常完成率也是 3/4。正常完成的三题均正确。Freeway 是截断未作答，不是明确识别为另一个游戏；其推理中的猜测不替代最终答案。

## 协议与审计

- 使用已安装 DeepSeek Harness 0.2.1-rc.5 的 headless 模式、自定义禁用插件配置。
- 系统指令严格为原作者的 `Answer the user's request.`。
- 四份用户消息为原始 prompt.txt 完整文本（读取时统一换行），没有附加候选、答案、我们的分析或新研究指导。
- 四次出站审计均通过；没有工具定义；每题一次模型调用；没有执行模型代码、反馈修正或重试。
- 配置为 thinking enabled、High；采用 Harness 的 Anthropic Messages 传输；服务默认采样，无 top_p 覆盖。
- 最大输出 32,768 tokens 为本项目本轮限制，不声称与 Astra 原始输出预算等价。Freeway 结果只说明这一设置下未完成，不能说明提高预算也不会识别。
- 用户后来明确要求禁止额外提示和工具；该约束与本批从开始采用的配置一致。

## 推理轨迹的初步观察

完整可见推理来自原始 SSE，未依赖可能截断字符串的 Harness JSON 事件投影。

Breakout 的推理多次检查输入行索引与通道映射，并修正部分定位；Pong 分析了代理、移动物体与前一帧通道；Pac-Man 尝试从代理通道权重还原空间布局。这些只是轨迹中的可观察策略，尚未逐项验证其数值、空间解释及因果有效性。

长推理不自动等于正确理解。本批 Freeway 的推理耗尽预算，提示“人工式逐行追踪大矩阵”可能有成本和索引错误风险；这一解释需要后续标注检验，不能凭一例下普遍结论。

## 用量与成本

服务返回输入计数合计 278,018，缓存读取计数 3,072，输出计数 116,398（不另重复加算推理）。根据 Messages 用量字段分项及核验价格，按峰时价格估计约 $0.2231；实际扣款以服务账单为准。总顺序运行时间约 10.39 分钟。

价格参考：https://api-docs.deepseek.com/quick_start/pricing/ 。本报告不包含密钥，原始轨迹不上传 Git。

## 与原文的比较边界

原文该组报告 Astra 4/4。本轮 Flash 为 3 个正确完成、1 个截断；两个结果存在模型、客户端、采样及输出预算差异。每个网络仅一次，不足以估计稳定成功率，也不足以宣称能力显著差异。

## 本地证据

目录：`H:\lm_understand_ds\runs\exp01\live_20261103T053114Z`。

每个网络保存 request.json、audit.json、source.json、response.sse、reasoning.md、answer.md、result.json；批次包含 summary.json、manifest.json 与实际覆盖配置。原始响应完整保留，包括最后一次截断。

下一步应先人工核对三份答案引用的权重与索引，并标注第四份轨迹的预算消耗。任何更高输出预算运行须另立条件，不能替换这次截断结果。未经新指示，不重复调用。
