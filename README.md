# lm_understand_ds

DeepSeek Flash 对 Weight-Space Programming 实验一的复现与可见推理分析。

截至2026-11-04：完成17次正式调用，覆盖High两种输出预算、Freeway独立重跑、关闭thinking及Max。全部无工具、使用原作者提示。

- [全部实验分析](reports/exp01_all_runs_synthesis.md)
- [完整结果与文件哈希索引](artifacts/exp01/index.json)
- [归档说明](artifacts/exp01/README.md)
- [Max最终验收](reports/exp01_max_final_acceptance.md)
- [关闭thinking分析](reports/exp01_no_thinking_analysis.md)
- [High完整批次比较](reports/exp01_output_budget_comparison.md)
- [Freeway重跑分析](reports/exp01_freeway_rerun_comparison.md)
- [研究方案（历史规划，不等同已实施内容）](RESEARCH_PLAN.md)
- [实验运行器](src/exp01.py)

High与Max完整批次均3/4，关闭thinking为0/4。正确标签不等于准确机制解释；详细限制见综合报告。Max阶段验收为历史快照，现以最终报告为准。

原研究及数据来源：[原作者日志](https://github.com/RikiyaT/lm_understand-logs)；固定commit `4d09ba6d6a7e891dd8063974dfe81b3d78e3494f`。本地工作目录 `H:/lm_understand_ds`。认证信息、依赖和mock不提交。
