# lm_understand_ds

DeepSeek Flash + High 对 Weight-Space Programming 原实验的协议级复现与推理轨迹分析。

- [研究方案 v3](RESEARCH_PLAN.md)
- [Pilot 配置清单](protocol/pilot_manifest.json)
- [复现差异登记](protocol/replication_differences.md)
- [轨迹标注规范](protocol/trajectory_annotation.md)

首期：原任务提示、自定义 DeepSeek Harness 模式、自建实验 Harness、隔离 Python Sandbox；优先保存并分析 reasoning_content、代码与反馈。后续再比较推理强度和 System Prompt。

**当前状态：仅完成方案与仓库初始化；尚未实现实验运行器，未运行模型实验。**

本地工作目录：`H:\lm_understand_ds`。`data/`、`runs/` 和认证信息不默认提交。付费批量任务前必须完成协议、接口及预算核验。

原研究：[博客](https://rikiyat.github.io/blog/weight-space-programming/) · [实验日志](https://github.com/RikiyaT/lm_understand-logs)。
