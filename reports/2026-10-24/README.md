# 2026-10-24 周五收盘更新与15只个股研究

最新入口：closing_update/monday_close_update_20261024.html。
完整15股事实研究：stock_deep_dive_risk_20261024.html 与 stocks/。
原报告保留其10/22历史收盘和10/23盘中时间戳，顶部链接到最新更新。

用户确认：已完成首次建仓，当前持有防守资产；按全部购买力可重新配置规划。只做多正股、单只不超过总净值20%、约12%组合回撤容忍度。2026-10-24用户已明确允许50%或80%现金；这是用户提供的信息，非独立比赛手册核验。当前WLS成员资格、实际持仓、净值仍需终端资料，未执行交易。

最新方案：首批上限20%股票/80%现金；确认阶段35%/65%；条件目标50%/50%。50%成分目标未变，35%为其股票权重乘0.7；不是收益最优模型。

周五更新数据：48个Longbridge常规时段last_done报价，时间戳2026-10-23 20:00:00/01 UTC，明确排除盘后。保留历史259收盘至10/22，再拼接10/23报价，得到260价格/259收益。历史按日接口权限拒绝301607，未独立验证历史bar。PG前收盘差0.005美元，已记录并做敏感性检查。

复现：在本目录运行 python closing_update/analyze_close.py，然后 python closing_update/build_close_report.py、python closing_update/finalize_close.py、python closing_update/validate_close.py。运行验证后视觉与浏览器计算器检查需要另行完成并记录，不能仅靠程序通过宣布视觉通过。

完整交付包：../stock_deep_dive_risk_20261024_close.zip，保留两日期依赖目录。
旧 risk_analysis.py 与 build_stock_report.py 为历史版本生成器，重跑会恢复旧时点内容；历史文件不应充当最新执行输入。
