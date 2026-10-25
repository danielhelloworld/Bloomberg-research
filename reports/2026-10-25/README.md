# 2026-10-25 扩展选股与10/26—10/30每日预选报告

用户新增授权：综合既有全球市场/15股研究，扩大候选数量，加入科技股超跌反弹，并为下周每天提供个股报告。目标覆盖55股（原15+新增40）。本轮是2026-10-25事前研究，不是未来各日已完成的收盘筛选，不创建新的定时任务，不执行交易。

用户约束沿用：已完成首次建仓、持有防守资产；按全部购买力可重新配置规划；只做多正股、单股<=20%总净值、可留50%或80%现金、约12%回撤容忍度。WLS资格、实际持仓与净值仍未提供。新增候选不是新增风险预算。

数据：data/fetch_1.json 为55股Longbridge报价，时间戳为10/23 20:00:00/01 UTC常规时段；fetch_2.json 为40新候选的5日/10日/半年涨跌及TTM估值；fetch_3.json 为40股静态信息。calc指标无独立行情时点，需与报价last_done核对，不能当成交指令。原15股已有历史指标保留原来源。

历史缺口：Longbridge历史接口前轮已权限拒绝，不重复尝试绕过；Financial Datasets独立历史源余额为0（fetch_0.json）；公开Yahoo历史接口首次两只探测403。均未购买额度或绕过权限，不继续重试。同一口径完整K线不可得，不为新增股编造RSI、ATR、52周回撤、相关性或回测成绩。短期跌幅仅构成研究筛选条件。

lanes/ 保存三条公司/事件证据研究。最终优先级、事件表和每日名单以根目录生成的综合HTML/结构化数据为准。

## Completed delivery

Entry: weekly_expanded_20261026_30.html. 55 stock pages,5 daily conditional previews,124 source records/120 unique URLs,18 event rows,17 confirmed-time ICS entries. Validation:62 HTML pages and1124 local links plus independent arithmetic, classifications, source references and time conversions. Desktop visual and filter checks passed; see validation.json.

Run analyze_expanded.py, build_expanded_report.py, validate_expanded.py to reproduce; reperform visual checks before recording pass and running package_expanded.py. Full packet ../expanded_equity_week_20261026_30.zip includes prior dated dependencies.

User confirmed five actual premarket updates. ACTIVE automation10-26-30 starts20:45 Asia/Shanghai onOct26–30 only, bounded5occurrences; saved configuration verified. See automation_schedule.json. Future daily pages currently remain Sunday previews until actual runs occur. No trades.
