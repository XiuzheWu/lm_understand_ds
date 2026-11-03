"""Deterministic post-hoc quote/index checks; never exposed to the research model."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/original/lm_understand-logs/exp1_which_game/networks/0bbcc3ea_actor.txt'
lines=source.read_text().splitlines()
start=next(i for i,x in enumerate(lines) if x.startswith('W1 ('))+1
rows=lines[start:start+500]
assert len(rows)==500 and all(len(r.split())==32 for r in rows)
samples=[
('-0.040 0.049 -0.012 -0.090','(2,1), ch0'),
('0.012 0.056 0.030 -0.107','(2,2), ch0'),
('4.822 -3.670 -2.966 3.749','bottom row, ch0'),
('5.095 -3.877 3.016 0.494','bottom row, ch0'),
('2.332 -3.398 -0.089 -0.126','(2,1), ch2'),
('4.331 -2.970 -1.338 -0.382','(2,2), ch2'),
('1.758 4.744 -2.013 2.320','(3,1), ch3'),
('-6.691 4.613 -1.051 4.396','(3,2), ch3')]
audit=[]
for quote,claimed in samples:
    hits=[i for i,r in enumerate(rows) if r.startswith(quote)]
    assert len(hits)==1
    i=hits[0]; audit.append({'quote_prefix':quote,'claimed':claimed,'actual_input_index':i,'actual_row':i//50,'actual_column':i//5%10,'actual_channel':i%5})
(ROOT/'reports/exp01_freeway_quote_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
table='\n'.join(f"| `{a['quote_prefix']}` | {a['claimed']} | {a['actual_input_index']} | ({a['actual_row']},{a['actual_column']}), ch{a['actual_channel']} |" for a in audit)
section=f'''\n## Freeway 错误解释的定位：权重引用与索引不一致

对新轮 Freeway 最终答案的八个选定引用进行精确前缀匹配。每个前缀在原 W1 的 500 行中唯一匹配。按原公式 i=(row×10+column)×5+channel 还原坐标，结果如下（均为零基索引）：

| 引用前缀 | 模型声称位置 | 实际输入索引 | 实际位置 |
|---|---|---:|---|
{table}

这些数值确实存在，但对应关系错误。模型用来支持“内部代理通道很弱”的两个例子实际来自障碍通道；用来支持“上方奖励目标”的两个例子实际来自代理通道；所谓底部代理例子位于第 6 行，而原提示定义底部可玩行为第 8 行。

因此，其“底部球拍＋上方砖块”的解释没有得到所引用权重的支持。长输出没有保证索引准确，也没有保证最终解释可靠。这是对选定引用的核验，不是对全部推理段落的完整审计；它证明证据对应错误，不单独证明这些错误是最终答案的唯一因果来源。

该检查在四题结束后执行，未把任何检查结果提供给 DeepSeek。它不构成研究模型工具使用。

## 行为比较的初步结论

- Breakout 本轮更短且正确，Pong/Pac-Man 本轮更长且正确；提高可用预算不必然导致每题输出增长。
- Freeway 从首轮截断变为本轮自行结束，但答案错误、置信度 88%；不能把完成率提高等同于识别准确率提高。
- 抽查轨迹可见逐行索引、权重抄录、反复校对和候选游戏比较。Freeway 的最终答案暴露了“数值读取正确但通道/位置对应错误”的具体失效方式。
- 这些结果支持继续研究信息定位与核验能力，但不支持凭本轮就断言 Flash 缺乏全部机制理解能力，或推断 Astra 的内部方法。
'''
report=ROOT/'reports/exp01_output_budget_comparison.md'
text=report.read_text(encoding='utf-8').split('\n## Freeway 错误解释的定位')[0]
report.write_text(text+section,encoding='utf-8')
print(table)
