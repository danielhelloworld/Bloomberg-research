"""Add dated navigation without overwriting the historical report calculations."""
from pathlib import Path
import re,json
P=Path(__file__).resolve().parent
base=P.parent; old=base.parent/'2026-10-23'
targets=[(base/'stock_deep_dive_risk_20261024.html','closing_update/monday_close_update_20261024.html'),(old/'global_market_positioning_20261026.html','../2026-10-24/closing_update/monday_close_update_20261024.html')]
targets += [(p,'../closing_update/monday_close_update_20261024.html#stock-'+p.stem) for p in (base/'stocks').glob('*.html')]
for path,url in targets:
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'<aside id="close-update-banner".*?</aside>','',text,flags=re.S)
    banner=f'<aside id="close-update-banner" style="background:#e6f0ea;color:#173e30;padding:18px 28px;border-bottom:3px solid #24856a;font:16px/1.7 sans-serif"><b>10/24新增周五收盘更新：</b>用户已确认允许50%或80%现金。<a style="color:#00685b" href="{url}">查看10/23常规时段收盘、三档仓位与最新风险复核 →</a> 本页原有数据和估值时间戳保留，最新执行判断以更新页为准。</aside>'
    text=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+banner,text,count=1)
    path.write_text(text,encoding='utf-8')
(base/'README.md').write_text('''# 2026-10-24 周五收盘更新与15只个股研究

最新入口：closing_update/monday_close_update_20261024.html。
完整15股事实研究：stock_deep_dive_risk_20261024.html 与 stocks/。
原报告保留其10/22历史收盘和10/23盘中时间戳，顶部链接到最新更新。

用户确认：已完成首次建仓，当前持有防守资产；按全部购买力可重新配置规划。只做多正股、单只不超过总净值20%、约12%组合回撤容忍度。2026-10-24用户已明确允许50%或80%现金；这是用户提供的信息，非独立比赛手册核验。当前WLS成员资格、实际持仓、净值仍需终端资料，未执行交易。

最新方案：首批上限20%股票/80%现金；确认阶段35%/65%；条件目标50%/50%。50%成分目标未变，35%为其股票权重乘0.7；不是收益最优模型。

周五更新数据：48个Longbridge常规时段last_done报价，时间戳2026-10-23 20:00:00/01 UTC，明确排除盘后。保留历史259收盘至10/22，再拼接10/23报价，得到260价格/259收益。历史按日接口权限拒绝301607，未独立验证历史bar。PG前收盘差0.005美元，已记录并做敏感性检查。

复现：在本目录运行 python closing_update/analyze_close.py，然后 python closing_update/build_close_report.py、python closing_update/finalize_close.py、python closing_update/validate_close.py。运行验证后视觉与浏览器计算器检查需要另行完成并记录，不能仅靠程序通过宣布视觉通过。

完整交付包：../stock_deep_dive_risk_20261024_close.zip，保留两日期依赖目录。
旧 risk_analysis.py 与 build_stock_report.py 为历史版本生成器，重跑会恢复旧时点内容；历史文件不应充当最新执行输入。
''',encoding='utf-8')
(base/'CONTINUATION.md').write_text('''# Continuation state — 2026-10-24 Friday close update

Latest report: closing_update/monday_close_update_20261024.html. All 15 original stock pages and original market report retained with dated update navigation. Friday close inputs, calculations and validation are inside closing_update/. Read its validation_close.json for exact completed checks.

Cash gap CLOSED: user explicitly confirmed 50% and 80% cash permitted on 2026-10-24. Do not ask again. Initial entry completed; existing defensive holdings; plan as if full buying power can be reallocated. Long only common stock, single name <=20% NAV, ~12% drawdown tolerance, not guaranteed loss cap. Current WLS eligibility, exact portfolio and NAV remain unavailable; no trades.

Reference: 20% starter maximum, 35% confirmation stage, 50% conditional target; no return optimization claim. Complete macro/individual stock work retained. Future continuation should address only unfinished validation or explicit new user steering, not automatically enlarge the universe.

The five-hour thread heartbeat id automation was created for quota recovery. It must use actual quota reset state, not purchase credits, reset tokens, change model or bypass limits. Once no authorized work remains, stop automatic continuation rather than invent new work. Desktop app/awake machine needed for local scheduled work.
''',encoding='utf-8')
print('Updated dated navigation in',len(targets),'historical report pages; README and continuation preserved latest constraints.')
