"""Compare preserved batches and verify that max_tokens is the sole wire change."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'runs/exp01/live_20261103T053114Z'
new=sorted((ROOT/'runs/exp01').glob('live_393216_*'))[-1]
before=json.loads((old/'summary.json').read_text())
after=json.loads((new/'summary.json').read_text())
assert len(after)==4, 'Wait until all four responses finish'
comparisons=[]
for a,b in zip(before,after):
    assert a['id']==b['id']
    ra=json.loads((old/a['id']/'request.json').read_text())
    rb=json.loads((new/b['id']/'request.json').read_text())
    changed=[k for k in set(ra)|set(rb) if ra.get(k)!=rb.get(k)]
    assert changed==['max_tokens'], changed
    assert ra['messages']==rb['messages'] and not rb.get('tools')
    assert json.loads((new/b['id']/'audit.json').read_text())['passed']
    comparisons.append({'id':b['id'],'game':b['true'],'changed_request_fields':changed,'old':a,'new':b})
table='\n'.join(f"| {a['true']} | {a['stop_reason']} / {a['usage']['output_tokens']:,} | {b['stop_reason']} / {b['usage']['output_tokens']:,} | {b['guess'] or '无最终答案'} | {b['confidence']} | {b['wall_seconds']:.1f} |" for a,b in zip(before,after))
uncached=sum(b['usage']['input_tokens'] for b in after)
cached=sum(b['usage'].get('cache_read_input_tokens',0) for b in after)
output=sum(b['usage']['output_tokens'] for b in after)
peak=(uncached*.3+cached*.006+output*1.2)/1e6
report=f'''# 实验一：首轮与服务最大输出预算比较

2026-11-03。旧批次 `{old.name}`；新批次 `{new.name}`。

## 结果

| 网络 | 首轮结束原因 / 输出 tokens | 新轮结束原因 / 输出 tokens | 新轮识别 | 自报置信度 % | 新轮秒 |
|---|---|---|---|---:|---:|
{table}

新轮正确最终回答：{sum(b['correct'] for b in after)}/4；正常结束：{sum(b['stop_reason']=='end_turn' for b in after)}/4。

## 配置一致性

逐题对比实际出站请求，唯一差异字段为 max_tokens：32,768 → 393,216。
系统提示、完整用户消息、Flash、High、无工具、默认采样均相同。每题重新开始且只有一次请求，没有追加提示、反馈、续写或重试。首轮结果原样保留。

新轮控制器取消单题总时限，保留网络无数据超时。服务最大输出预算不是无限长度；是否自行结束由 stop_reason 判断。

## 成本与证据

新轮非缓存输入 {uncached:,} tokens，缓存读取 {cached:,} tokens，输出 {output:,} tokens。按核验峰时价格估计 ${peak:.4f}，不是服务账单。

本地完整记录：`H:\\lm_understand_ds\\runs\\exp01\\{new.name}`。保存原始 SSE、可见推理、答案、实际请求、审计与评分。原始轨迹不上传 Git。

## 解释边界

每个网络、每个预算只有一次采样。差异不能全部归因于预算；服务采样与缓存状态也应记录。长推理和正确游戏名称均不足以证明内部计算机制已经被准确还原。机制解释需核对权重证据，而非依据叙述流畅度评分。
'''
(ROOT/'reports/exp01_output_budget_comparison.md').write_text(report,encoding='utf-8')
(ROOT/'reports/exp01_output_budget_comparison.json').write_text(json.dumps(comparisons,ensure_ascii=False,indent=2),encoding='utf-8')
print(report)
