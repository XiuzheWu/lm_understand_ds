# 环境与 Prompt 初步核验

日期：2026-11-03。范围：已下载原仓库并读取关键配置；尚未配置 DeepSeek 插件，尚未调用模型。

## 原材料

- 本地目录：`H:\lm_understand_ds\data\original\lm_understand-logs`
- 来源：https://github.com/RikiyaT/lm_understand-logs
- 固定提交：`4d09ba6d6a7e891dd8063974dfe81b3d78e3494f`，detached HEAD。
- 原仓库独立保存，由项目的 `data/` 忽略规则排除，不重复上传第三方大文件。

## 已核验的关键设置

1. `harness/instructions.md` 原文为 `Answer the user's request.`，作为首组系统指令。
2. `harness/codex_config.toml` 的默认模型是 luna/medium，但实际实验调用覆盖默认值；不能把默认配置误认作实验模型配置。
3. 原始内置 shell、网页、插件、子代理等功能关闭。我们应通过专用外部执行链提供实验权限。
4. `harness/sandbox.py` 是围棋实验的 Linux/bubblewrap 沙箱，含占位路径与任务专用 prelude，不能直接作为八组通用运行器。
5. **实验 3 每次 Python 调用是新进程，不保留变量**；预加载 np 与 W，可用 100 次，每次 600 秒，返回输出上限 20,000 字符。仅允许权重线性代数分析，禁止前向和联网。
6. 实验 4 无工具、单次回答；生成代码后运行并反馈将违反其原始条件。

## 首轮 Prompt 入口

以下路径均相对于原仓库，正式运行从文件读取完整内容，不能用摘要代替。

| 条件 | 原始入口 |
|---|---|
| 游戏识别 Breakout | `exp1_which_game/runs/breakout/prompt.txt` |
| 语言识别 Python | `exp3_language/runs/python_r0/message.txt` |
| 汽车修复 | `exp4_fix_car/runs/oneshot_repair/reply/prompt.txt` |
| 数学修复 50 次 | `exp8_math/runs/p50c/turns/t001/prompt.txt` |

实验 1、4 的提示含大量原始权重，必须先按 Flash tokenizer/接口限制核验容量，不能静默裁剪。实例路径里的答案标签仅用于控制器登记，不能额外暴露给研究模型。

## 宿主环境

- Windows Python 3.11.4、Node v20.15.1 已检测到。
- 已检测到 DeepSeek Harness 安装文件；版本、插件配置和请求审计能力尚未核验。
- WSL 已注册 Ubuntu-24.04，实际检测到 `/usr/bin/python3`（3.12.3）和 `/usr/bin/bwrap`；实际沙箱隔离能力仍需测试，二进制存在不等于隔离已验收。
- 当前 PATH 未检测到 Docker；这不等于机器上一定未安装 Docker。

输入规模：实验 1 Breakout 提示 116,093 字节，实验 3 Python 提示 6,679 字节，实验 4 提示 579,340 字节。字节数不是 Token 数；实验 4 尤其需要先核验上下文容量。

## 下一步配置顺序

1. 固定 DeepSeek Harness 版本，建立 Replication 独立模式，不修改用户默认模式。
2. 验证实际系统指令为原文，关闭无关注入；模型 Flash，thinking enabled，high。
3. 保留原代码块协议并完整保存 reasoning_content；明确历史推理字段的 API 行为。
4. 按实验配置沙箱状态：实验 3 fresh process；其他任务按各自规则决定文件/变量持久化。
5. Linux 中安装/验证所需依赖及 bwrap，检查断网、只读权重、工作目录与资源限制。
6. 先用固定伪响应测试解析、预算和日志，再进行小额接口预检；费用上限未设前不启动批量实验。

以上是配置路线，不代表运行器已实现或隔离已通过验收。
