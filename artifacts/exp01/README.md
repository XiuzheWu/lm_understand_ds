# 正式运行归档

按原始批次时间戳和网络ID组织，index.json包含17次调用及文件原始SHA256。reasoning.md和answer.md是原样副本；空reasoning表示没有返回独立推理。response.sse.gz为原始响应流；request.json.gz为实际出站请求；client_request.json.gz仅在网关修改thinking/effort时存在。gzip只压缩，不修改内容。

批次053114为High 32768；055320为High最大预算；064141为单独Freeway重跑；082916为关闭thinking；113950为Max。所有日期为2026-11-03，目录时间戳是UTC，报告整理日期按Asia/Singapore。

四个网络ID：a9f535cc=Breakout，dfc6cb65=Pong，bdf99279=Pac-Man，0bbcc3ea=Freeway。标签只供评分，没有作为候选列表发给研究模型。

原作者数据来自RikiyaT/lm_understand-logs，具体来源见source.json。manifest的effort字段表示实验条件，最终以request.json为准；Freeway单独重跑manifest沿用4次上界，实际仅一次，见rerun_design.json。

不含密钥、HTTP认证头、临时客户端家目录或模拟结果。原始本地文件仍保留。报告为事后分析，没有反馈给实验模型。
