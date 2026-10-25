# 进攻型股票研究 — 2026-10-25

用户新增请求：再研究一些进攻资产。仍为Bloomberg Trading Challenge，只多正股、单名<=20%总净值、用户允许50%/80%现金、约12%回撤容忍。已有防守持仓，按全购买力可重新配置规划；WLS和实际账户明细未提供。此轮不交易，不创建新自动任务。

范围：28个进攻候选=原55池12只重新定位+16新公司。新公司ALAB MRVL CRWV NBIS GEV SNDK STX WDC TSLA HOOD COIN MSTR RKLB ASTS TEM HIMS。不含ETF/期权/直接加密币。COIN/HOOD/MSTR虽为股票，仍有加密、融资或企业杠杆风险，不能视为无杠杆或不同因子分散。

新16股常规时段行情、5/10日/半年涨跌和供应商TTM在data/snapshot_0/1/2.json。报价时点10/23 20:00:00/01UTC；抓取10/25。旧12股数据和公司事实沿用../expanded_research.json，保留证据时点。不重试受限历史，不编RSI/ATR/beta/covariance或回测收益。分析师的预期差、主观冲击与公司事实分别标示。

建议进攻预算属于既有风险预算：首次总试仓<=2%且在原20%首批股票预算内；确认后进攻总预算最多8%，与既有科技AI8%是同一预算，不能叠加。三种篮子只是互斥研究情景，不是自动订单。高风险叙事型拟更小且单列。未核验资格/实际披露/估值/报价时不具备直接执行条件。

已有10/26–30 20:45盘前更新任务id10-26-30仍按原已授权55股范围工作。本轮新增16股作为独立研究，不暗中扩大自动调度范围。

## Completed delivery

Entry aggressive_equity_20261025.html;28individual pages,16new companies,71combined unique company coverage,62source records/URLs,8event rows including MUdividend distinctly labeled. validation.json passed30HTML/492local links, math/time/source checks, browserlayout andcalculator. IndependentQA andresolutions inlanes/qa_attack.md andCONTINUATION.md.

Reproduce analyze_attack.py,build_attack_report.py,validate_attack.py; reperform visual/calculator checks before recording pass and package_attack.py. Fullpacket ../../aggressive_equity_research_20261025.zip retains priorresearch dependencies. No trades or scheduler changes.
