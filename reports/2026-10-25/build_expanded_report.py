from pathlib import Path
import json,html,re,datetime,csv
P=Path(__file__).resolve().parent
A=json.loads((P/'expanded_research.json').read_text(encoding='utf-8'))
M=A['metrics']; NEW=A['new_stocks']; OLD=A['legacy_stocks']; SOURCES={s['id']:s for s in A['sources']}
E=lambda x:html.escape(str(x),quote=True)
def text(x):
    if isinstance(x,list):return '；'.join(map(text,x))
    if isinstance(x,dict):return '；'.join(str(k)+'：'+text(v) for k,v in x.items())
    return '' if x is None else str(x).replace('根代理价格筛选','本次价格筛选').replace('根代理','本次研究')
def f(x,n=2):return '—' if x is None else f'{x:,.{n}f}'
def pct(x):return '—' if x is None else f'{x:+.2f}%'
def ref(id,prefix=''):
    s=SOURCES.get(id)
    return f'<a class="ref" href="{prefix}sources.html#{E(id)}">{E(id)}</a>' if s else '<span class="muted">来源待核</span>'
def refs(ids,prefix=''):return ' '.join(ref(id,prefix) for id in ids)
def safe(t):return t.replace('.','_')
def stocklink(t,prefix=''):return f'<a href="{prefix}stocks/{safe(t)}.html">{t}</a>'
def table(head,rows,id=None):return '<div class="scroll"><table'+(f' id="{id}"' if id else '')+'><thead><tr>'+''.join('<th>'+h+'</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def section(id,title,body):return f'<section id="{id}"><h2>{title}</h2>{body}</section>'
css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f6f7f5;color:#19332f;font:16px/1.85 "Segoe UI","Microsoft YaHei",sans-serif}main{max-width:1240px;margin:auto;padding:40px 38px 90px}header{border-bottom:4px solid #19735c;padding:25px 0 32px}h1{font-size:40px;line-height:1.38;letter-spacing:-.7px;margin:14px 0 22px}h2{font-size:27px;line-height:1.5;margin:0 0 20px}h3{font-size:21px;margin:19px 0 10px}p{margin:14px 0 20px}a{color:#006e60;text-underline-offset:4px}.eyebrow{font-size:13px;letter-spacing:1.8px;font-weight:700;color:#247861}.lede{font-size:19px;max-width:1020px}.meta,.muted{font-size:13px;color:#64786d}.notice{background:#e7efe8;border-left:4px solid #197d61;padding:18px 22px;margin:23px 0}.warning{background:#f8eddd;border-color:#b57d35}nav{display:flex;flex-wrap:wrap;gap:9px 22px;padding:20px 0}section{padding:42px 0 27px;border-bottom:1px solid #d5e1d7;scroll-margin-top:25px}.scroll{overflow-x:auto;margin:20px 0}table{width:100%;border-collapse:collapse;background:white;font-size:14px}th,td{padding:12px 13px;text-align:left;vertical-align:top;border-bottom:1px solid #e4e9e4}th{background:#e2ece4;color:#294b3c}tr:nth-child(even) td{background:#fafbf9}.ref{display:inline-block;font-size:12px;margin-right:7px}.funnel{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:28px 0}.funnel div{border-top:3px solid #3c8a6a;padding:14px;background:white}.funnel b{display:block;font-size:30px}.badge{font-size:12px;border:1px solid #b9cfbd;border-radius:3px;padding:2px 7px;display:inline-block;white-space:nowrap}.daystrip{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.daystrip a{background:#e4eee6;padding:15px;text-decoration:none}.daystrip strong{display:block}article{border-top:1px solid #d9e4dc;padding:20px 0 28px}.barrow{display:grid;grid-template-columns:80px 1fr 70px;gap:12px;align-items:center;font-size:14px;height:32px}.bartrack{background:#edf2ee;height:14px;position:relative}.bartrack i{position:absolute;height:14px;background:#b54d3c;right:0}.bars{background:white;padding:24px;margin:25px 0}.filters{display:flex;flex-wrap:wrap;gap:15px;margin:20px 0}label{display:block}input,select,button{font:inherit;padding:8px 11px;border:1px solid #b5cebd;border-radius:3px;background:white}button{background:#1b7158;color:white;cursor:pointer}.compact{font-size:14px}li{padding:4px 0 9px}.source{overflow-wrap:anywhere}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:25px}footer{font-size:13px;color:#6e7e72;padding:25px 0}@media(max-width:750px){main{padding:18px 17px 50px}h1{font-size:29px}h2{font-size:24px}.lede{font-size:17px}.funnel{grid-template-columns:1fr 1fr}.daystrip{grid-template-columns:1fr}.grid2{grid-template-columns:1fr}th,td{padding:10px;min-width:88px}.filters{display:block}.filters label{margin:10px 0}}@media print{body{background:white}main{max-width:none;padding:0}nav,.filters{display:none}article{break-inside:avoid}table{font-size:10px}th,td{padding:6px}.daystrip{display:block}}'''
common_notice='研究对象不等于买入清单。只做多正股，单股不超过总净值20%；允许50%或80%现金，约12%回撤容忍度。现有防守资产按可全额重配规划，实际持仓、账户净值和当日WLS资格尚缺。TSM、ARM、TM等存托凭证须另外核对比赛是否允许；若不允许则移出，空余留现金。新增候选不能叠加扩大既有风险预算。'
def page(title,body,prefix='',subtitle='2026-10-25 事前研究 · 行情截至10/23常规时段'):
    nav=f'<nav><a href="{prefix}weekly_expanded_20261026_30.html">综合入口</a><a href="{prefix}weekly_expanded_20261026_30.html#daily">五天报告</a><a href="{prefix}weekly_expanded_20261026_30.html#board">55股筛选表</a><a href="{prefix}weekly_expanded_20261026_30.html#risk">风险预算</a><a href="{prefix}sources.html">证据登记</a></nav>'
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+'</title><style>'+css+'</style></head><body><main><header><div class="eyebrow">BLOOMBERG TRADING CHALLENGE · 扩展选股</div><h1>'+E(title)+'</h1><p class="meta">'+E(subtitle)+'</p></header>'+nav+body+'<footer>本报告不执行交易。筛选阈值和风险冲击是研究假设，不是经验证的获利规则、概率预测或最大亏损保证。</footer></main></body></html>'

events=[]
def event(t,date,title,window,call,source,confidence='confirmed',note=''):
    et=datetime.datetime.fromisoformat(date+'T'+call) if call else None
    cn=et+datetime.timedelta(hours=12) if et else None
    events.append({'ticker':t,'date_et':date,'title':title,'release_window':window,'call_time_et':call,'beijing_call':cn.strftime('%m/%d %H:%M') if cn else None,'source_id':source,'confidence':confidence,'note':note})
event('MACRO','2026-10-27','消费者信心','数据10:00 ET','10:00','ROOT-TCB')
event('V','2026-10-27','FY26Q4业绩','盘后','17:00','IC_V_EVENT')
event('VRT','2026-10-28','Q3业绩','盘前，精确分钟未核','11:00','IC_VRT_EVENT')
event('MACRO','2026-10-28','FOMC决议','决议14:00 ET','14:00','ROOT-FED')
event('MACRO','2026-10-28','美联储发布会','发布会14:30 ET','14:30','ROOT-FED')
event('GOOGL','2026-10-28','Q3业绩','电话会前发布，精确分钟未核','16:30','ROOT-GOOGL-EVENT','medium_indexed','公司公告分发索引可读，正文403；交易所评论交叉确认日期，具体时间仍须终端核验')
event('NOW','2026-10-28','Q3业绩','盘后','17:00','SP_NOW_DATE')
event('KLAC','2026-10-28','FY27Q1业绩','盘后','17:00','SEM-KLAC-2')
event('MSFT','2026-10-28','FY27Q1业绩','盘后','17:30','ROOT-MSFT-EVENT')
event('CAT','2026-10-29','Q3业绩','06:30 ET发布','08:30','IC_CAT_EVENT')
event('MACRO','2026-10-29','Q3 GDP初值 + 9月PCE相关数据','数据08:30 ET','08:30','ROOT-BEA')
event('MA','2026-10-29','Q3业绩','精确首次发布时点未核','09:00','IC_MA_EVENT')
event('LLY','2026-10-29','Q3业绩','精确首次发布时点未核','10:00','IC_LLY_EVENT')
event('AMZN','2026-10-29','Q3业绩','盘后，电话会17:00 ET','17:00','ROOT-AMZN-EVENT')
event('INTC','2026-10-29','Q3业绩','盘后','17:00','SEM-INTC-2')
event('XOM','2026-10-30','Q3业绩','06:30 ET发布','09:30','ROOT-XOM-EVENT')
event('ABBV','2026-10-30','Q3业绩','盘前，精确分钟未核','09:00','ROOT-ABBV-EVENT')
event('CVX','2026-10-30','Q3业绩','电话会前发布，精确分钟未核','11:00','ROOT-CVX-EVENT')
for e in events:
    assert e['source_id'] in SOURCES,e
events.sort(key=lambda e:(e['date_et'],e['call_time_et']))
(P/'event_register.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
with (P/'event_register.csv').open('w',encoding='utf-8-sig',newline='') as file:
    wr=csv.DictWriter(file,fieldnames=list(events[0]));wr.writeheader();wr.writerows(events)
ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Bloomberg Research//Conditional Event Research//ZH','CALSCALE:GREGORIAN']
for i,e in enumerate(events):
    if e['confidence']!='confirmed':continue
    dt=datetime.datetime.fromisoformat(e['date_et']+'T'+e['call_time_et'])+datetime.timedelta(hours=4)
    # All exported events are in EDT week; exact calls/data only, not unknown release minutes.
    start=dt.strftime('%Y%m%dT%H%M00Z');end=(dt+datetime.timedelta(minutes=30)).strftime('%Y%m%dT%H%M00Z')
    ics+=['BEGIN:VEVENT',f'UID:btc-{e["date_et"]}-{e["ticker"]}-{i}@local-research','DTSTAMP:20261024T180000Z','DTSTART:'+start,'DTEND:'+end,'SUMMARY:'+e['ticker']+' '+e['title']+'（电话会/数据时点）','DESCRIPTION:预设监测事件，非下单安排；首次发布与电话会可能不同。','URL:'+SOURCES[e['source_id']]['url'],'END:VEVENT']
ics+=['END:VCALENDAR']
(P/'confirmed_events.ics').write_text('\r\n'.join(ics)+'\r\n',encoding='utf-8')

def factlist(s,prefix=''):
    return '<ul>'+''.join('<li>'+E(text(x['claim']))+' '+ref(x['source_id'],prefix)+'</li>' for x in s['facts'])+'</ul>'
def cleanparagraph(value,prefix=''):
    # Source tokens remain readable and resolve to the common ledger.
    out=E(text(value))
    for id in sorted(SOURCES,key=len,reverse=True):
        for brackets in [('[' ,']'),('【','】')]:
            out=out.replace(E(brackets[0]+id+brackets[1]),ref(id,prefix))
    return out
def stocksummary(t,prefix=''):
    if t in NEW:
        s=NEW[t]
        return f'<p><b>修复逻辑：</b>{cleanparagraph(s["rebound_case"],prefix)}</p><p><b>第一否决：</b>{cleanparagraph(s["kill"],prefix)}</p>'
    s=OLD[t]
    return f'<p><b>原论点：</b>{E(s["case"])}</p><p><b>第一否决：</b>{E(s["kill"])}</p>'
def metricsrow(t,prefix=''):
    m=M[t]
    return [stocklink(t,prefix),E(m['name']),E(m['price_bucket']),f(m['close']),pct(m['r1']),pct(m['r5']),pct(m['r10']),pct(m['r_halfyear']),f(m['pe_ttm']) if m['pe_ttm'] is not None and m['pe_ttm']>0 else 'NM' if m['pe_ttm'] is not None else '—']
head=['股票','名称','价格分类','10/23收盘$','周五','5日','10日','半年','供应商TTM P/E']

prioritynotes={
'NVDA':'10日-7.99%属于温和回撤，不满足本报告急跌阈值；收入仍强，但应收与投资收益使现金质量成为首要核查。',
'TSM':'10日-7.68%，5日已转正；属于回踩确认，不追逐第一轮反弹。台币报表与美元ADR估值要同口径。',
'AVGO':'10日-11.03%，半年-23.14%；主营AI与现金流提供证据，客户集中和高预期仍可能抵销修复。',
'META':'10日-10.58%，财报已出；把一次性诉讼、广告经营与负FCF拆开。拟于2027年建立无投票权Class C股份也带来治理与潜在稀释问题，详见个股页，不能当成本周已实施事件。',
'ANET':'10日-20.47%，有营收和现金支持；11/3自身财报前，先用云客户披露验证采购节奏。',
'NFLX':'10日-6.33%、半年-29.06%；广告下修与FCF交易因素要分别处理，不能把所有下调归为暂时影响。',
'LRCX':'10日-27.83%；10/21已经披露新季，不能编造下周新财报催化，重点检验供给瓶颈而非只看强EPS。',
'VRT':'10日-19.96%、半年-39.58%；等待周三盘前业绩和11:00 ET电话会，不为急跌而承担公告跳空。',
'MU':'10日-14.70%，半年仍+82.23%；可能是大涨后的估值消化，低TTM P/E还含存储周期顶部利润。',
'ASML':'10日-11.71%；核对订单、现金与出口限制，季度完整FCF有缺口，不能仅凭先进制程叙事。',
'AMAT':'10日-25.60%；设备资本开支和中国敞口是实际约束，价格确认须晚于基本面排雷。',
'KLAC':'10日-25.55%；6月已10拆1，需拆后EPS；周三财报前不把跌幅当安全边际。',
'AMD':'10日-15.02%，半年+69.26%；高增长需要兑现，供应商TTM倍数高，11/3自身业绩在下一周。',
'ORCL':'10日-10.78%、半年-27.92%；RPO不等于现金，负FCF和股权融资使它属于融资约束反弹。',
'ARM':'10日-21.01%，TTM倍数高；授权时点、关联方和SBC质量优先于低位接盘。',
'INTC':'10日-16.94%；亏损分母不算便宜，周四盘后财报前等待，周五重做现金与代工亏损判断。'}

body='<p class="lede">候选池扩大至55只：原B方案15只 + 新增40只。优先研究“基本面有支撑的价格修复”，同时保留软件反弹后的回踩、已公布业绩后的修复和非科技轮动对照。</p><div class="notice">'+common_notice+'</div>'
body+='<div class="funnel">'+''.join('<div><b>'+str(v)+'</b>'+E(k)+'</div>' for k,v in A['funnel'].items())+'</div><p class="meta">上面四类仅统计新增40只。分类依据是5日/10日供应商涨跌幅，不是RSI超卖认定；同一行业的多个股票仍可能只有一种共同风险。</p>'
body+=section('priority','先看这16只：研究顺序，不是买入排名',table(['股票','为何值得继续研究','升级为候选前的证据'],[[stocklink(t),E(prioritynotes[t]),E(text(NEW[t]['trigger']))] for t in A['research_priority'][:16]])+'<p><b>第一组研究优先：</b>NVDA、TSM、AVGO、META、ANET、NFLX；其中NVDA/TSM/NFLX不满足本报告10日≤-10%的急跌阈值，仍保留作质量修复对照。<b>事件验证优先：</b>VRT、KLAC、NOW、INTC。没有完整正常化估值和可靠预期修正数据，因此“研究优先”不代表已证实低估。</p>')
body+=section('daily','下周每一天：五份独立的条件预选报告','<p>所有报告都在10月25日编制。周二至周五的结果仍依赖届时真实行情、公告和前一交易日收盘；本轮不虚构未来价格、业绩结果或已发生的信号。</p><div class="daystrip">'+''.join(f'<a href="days/day_{d["date"].replace("-","")}.html"><strong>{d["label"]} · {d["date"][5:]}</strong>{E(d["theme"])}</a>' for d in A['days'])+'</div>'+table(['交易日ET','当日先研究','需等待的事件池','当天筛选重点'],[[f'<a href="days/day_{d["date"].replace("-","")}.html">{d["date"]} {d["label"]}</a>',' / '.join(d['focus']),' / '.join(d['wait']),E(d['rule'])] for d in A['days']]))

decliners=sorted([t for t in NEW if M[t]['r10']<=-10],key=lambda t:M[t]['r10'])
bars=''.join(f'<div class="barrow"><span>{t}</span><div class="bartrack"><i style="width:{abs(M[t]["r10"])/30*100:.2f}%"></i></div><b>{pct(M[t]["r10"])}</b></div>' for t in decliners)
body+=section('rebound','急跌筛选：跌得多只是入口','<div class="bars"><h3>10日跌幅达到10%的新增候选</h3>'+bars+'<p class="meta">来源：Longbridge calc指标；抓取于10/25，报价last_done与10/23常规时段收盘相符。每项指标精确起止时点未独立给出。</p></div>'+table(['类型','筛选条件（主观阈值）','代表','主要陷阱'],[
 ['短期急跌待确认','10日≤-10%，5日≤0','ANET / AVGO / META / LRCX / VRT','盈利预期仍可能下修；不把急跌当反转完成'],
 ['已反弹等待回踩','10日<0%，5日>0','TSM / PANW / CRWD / DDOG / SNOW','首轮修复已发生，追高会恶化盈亏比'],
 ['温和回撤观察','-10%<10日<0%，5日≤0','NVDA / NFLX / UBER / BAC','没有深度超跌证据，只能作为相对质量比较'],
 ['非超跌 / 强势对照','10日≥0%','AAPL / CRM / ADBE / NOW / ZS / V / MA','不能为满足反弹主题而硬贴超跌标签']])+'''<ol><li><b>基本面排雷：</b>先检查业绩/指引是否下降、现金是否依赖预收/融资/投资收益、是否有出口/法律/客户集中事件；没有合理解释就停留观察。</li><li><b>价格确认：</b>默认开盘至少30分钟后，检查30分钟收盘能否站回参考前一交易日高点，同时相对QQQ/SMH不再走弱；成交量需用同一时段过去均量比较，不能拿早盘量与全天均量机械相比。</li><li><b>不追跳空：</b>较最新完整收盘高开超过3%，等待回踩或下一日；跌破最新完整交易日低点则取消该次反弹触发。价格阈值是管理假设，未做参数优化。</li><li><b>事件闸门：</b>未来24小时有已确认财报时，新事件仓默认0；公告后重新读数据再判断。不能把结果“高于预期”写入尚未发生的日报。</li><li><b>动态锚点：</b>周一可用10/23高低点；周二起必须换成最新完整交易日高低点。五天报告里的10/23数值只是历史参考，不是整周不变的订单价。</li></ol><p>完整K线不可得，新增股没有可靠RSI、ATR、52周高点回撤和相关性估计。缺少这些字段不会被填成0，也不会通过重复尝试受限接口来补齐。研究不构成已验证的择时策略。</p>''')

boardorder=A['research_priority']+list(OLD)
boardrows=[]
for t in boardorder:
    row=metricsrow(t);boardrows.append(row)
body+=section('board','55股候选总表：可按名字和价格类型筛选','<p class="meta">价格与日涨跌：data/fetch_1.json，10/23常规时段。新股5/10日、半年与TTM：fetch_2.json；原15股5/10日沿用前稿对齐历史。PE不是统一正常化盈利，禁止直接跨列排序作估值结论。原15股不在本次TTM快照内，显示“—”。</p><div class="filters"><label>搜索股票或名称 <input id="search" placeholder="例如 NVDA、ANET、微软"></label><label>价格分类 <select id="bucket"><option value="">全部类型</option>'+''.join('<option>'+E(s)+'</option>' for s in A['funnel'])+'</select></label><span id="count" class="meta">55 / 55</span></div>'+table(head,boardrows,'candidate-board')+'<p>负盈利TTM显示NM；极高正P/E可能由接近零的GAAP分母造成。PANW、CRWD、DDOG等需结合SBC、收购、摊销及非GAAP调节，不能把一个供应商倍数当成可比估值。KLAC拆股已单独核对，不能把拆股当暴跌。</p>')

eventrows=[[e['date_et'],E(e['ticker']+' '+e['title']),E(e['release_window']),e['call_time_et']+' ET',e['beijing_call'],('已确认' if e['confidence']=='confirmed' else '索引/交叉证据，时间待复核'),ref(e['source_id'])] for e in events]
body+=section('calendar','事件登记：发布日期、电话会和北京时间分开',table(['日期ET','事件','首次发布窗口','电话会/数据','北京时间','置信度','证据'],eventrows)+'<p>全表10/26—10/30处于美国夏令时，北京比纽约快12小时；CAT与XOM发布06:30 ET即北京时间18:30。美股常规开盘21:30，收盘次日04:00。11/1以后改用13小时时差，AAPL/PLTR下一周事件不能沿用本周换算。</p><p><a href="confirmed_events.ics">下载已确认时点日历</a>：仅包含明确电话会或数据时间，排除GOOGL中置信精确时点；不是新闻稿首次发布分钟的保证，也不是交易任务。Apple11/2目前为官方索引证据、正文尚待复核；META、NFLX、LRCX、GE、RTX等已披露，不重复列作下周待发财报。</p>')

stressrows=[[f(r['replacement_tech_pct']),f(r['cash_pct']),pct(r['tech_shock_pct']),pct(r['tech_NAV_impact_pct']),pct(r['combined_NAV_impact_pct'])] for r in A['replacement_stress']]
body+=section('risk','增加选股数量，同时锁住风险预算',table(['约束','本轮研究纪律'],[
 ['首批总股票预算','仍以20%总净值为上限；新增反弹试仓总计最多2%，必须占用已有预算，不能再加在原20%上'],
 ['单股试仓','先以0.5%作为研究性示例，确认后最多1%；缺WLS、价格或事件验证则0。用户20%是合规上限，不是建议买到20%'],
 ['反弹子预算','证据确认后最多4%总净值；最多同时4只、每只最多1%，控制监测负担'],
 ['共同科技风险','MSFT/GOOGL/AMZN/ETN以及新增半导体、软件、网络、散热、AI相关电力，合并观察上限8%总净值；与4%反弹子预算为包含关系'],
 ['总股票条件目标','仍不高于50%；35%和50%需宏观与个股验证。未验证部分留现金'],
 ['回撤控制','沿用4%停止新增、6%复核并参考股票≤35%、8%参考≤20%、10%压低风险；12%触及容忍预算。跳空可能直接越过阈值'],
 ['组合与订单','全部原持仓+未成交买单合并计算；每增加一个新名字必须说明削减哪个旧预算或现金，不能把55只视作等权持仓']])+'''<p><b>一个可核算的替换压力例子：</b>原条件目标50%中，移出MSFT5%与GOOGL3%，其余42%作为参考核心；这42%在原“需求衰退”向量下损失约7.53%净值。以不同总额的新增科技股替换该8%预算，统一施加-20%、-35%、-50%冲击，得下表。</p>'''+table(['新增科技总额%','现金%','科技统一冲击','科技净值影响','加上参考核心后的净值影响'],stressrows)+'''<p>科技总额8%、下跌50%时，合计约损失11.53%净值，距离12%仅0.47个百分点，未计更坏的核心损失、流动性与费用，余量很薄。这支持先用小规模验证，而非因为候选多就买满。</p><p>该例不是新组合的预测回撤，核心冲击沿用旧假设，新科技统一冲击由研究者设定。完整新股历史缺失，<b>没有为新篮子计算可信的协方差、年化波动或回测收益</b>；旧50%组合的9.32%情景损失不能直接复制成新科技组合的风险结论。</p><p>若所有持有股票上涨10%，20%/50%股票仓位约贡献2%/5%组合收益，现金会产生明显相对收益拖累。保守风险预算与比赛排名冲刺之间存在真实取舍，本报告不保证两者同时最优。</p>''')

body+=section('sources','证据、下载和旧报告',f'<p>本轮共有{len(A["sources"])}条来源记录、{len(set(s["url"] for s in A["sources"]))}个去重URL，其中保留旧15股43条来源记录。公司披露、官方日历、公司公告分发索引和交易所评论分别标注；索引证据不冒充正文已读。</p>'+table(['文件','用途'],[
 ['<a href="sources.html">完整来源登记</a> / <a href="sources.json">JSON登记</a>','每条事实和日期的来源、期间与证据类型'],
 ['<a href="candidate_metrics.csv">55股指标CSV</a> / <a href="daily_preselection.csv">60条日期—股票预选</a>','可导入团队研究台账；不是订单文件'],
 ['<a href="event_register.csv">事件登记CSV</a> / <a href="expanded_research.json">完整结构化研究</a>','含缺口、主观假设、来源和压力向量'],
 ['<a href="validation.json">验证记录</a>','数据行数、日期、计算、引用、链接与页面检查'],
 ['<a href="../2026-10-24/closing_update/monday_close_update_20261024.html">上一轮周五收盘与配置报告</a>','20/35/50阶段和原15股风险依据，保留原时间戳'],
 ['<a href="../2026-10-24/stock_deep_dive_risk_20261024.html">原15股详细研究</a>','完整原始财务拆分；旧估值不当作新价格估值']])+'''<p>数据覆盖限制：Financial Datasets历史接口余额为0；Longbridge历史接口前轮权限不足；公开Yahoo历史首次探测403。未购买额度、未规避权限。当前可完成价格筛选、公司事实及事件研究，仍缺WLS当前成员/基准、实际账户及完整同口径历史。</p><p>后续每个交易日应替换最新报价、前收盘/高低点、实际财报与官方日历后重新运行筛选；本轮五份日报是已写好的事前研究模板与名单，不表示未来更新已执行。用户已确认并已创建10月26日至30日每天北京时间20:45的五次盘前更新任务；仅研究、不下单，五天后停止。任务已安排，但未来各次更新尚未执行。</p>''')
script='''<script>const rows=[...document.querySelectorAll('#candidate-board tbody tr')];function filter(){const q=document.querySelector('#search').value.trim().toLowerCase(),b=document.querySelector('#bucket').value;let n=0;for(const row of rows){const match=row.innerText.toLowerCase().includes(q)&&(!b||row.cells[2].innerText===b);row.hidden=!match;if(match)n++;}document.querySelector('#count').textContent=n+' / '+rows.length;}document.querySelector('#search').addEventListener('input',filter);document.querySelector('#bucket').addEventListener('change',filter);</script>'''
doc=page('55股扩展研究与下周五天预选报告',body)
(P/'weekly_expanded_20261026_30.html').write_text(doc.replace('</body>',script+'</body>'),encoding='utf-8')

(P/'stocks').mkdir(exist_ok=True)
for t,m in M.items():
    title=t+' · '+m['name']+' 个股研究'
    b=f'<p class="lede">{E(m["price_bucket"])} · '+('新增研究对象' if t in NEW else '原15股延续研究')+'</p><div class="notice">'+common_notice+'</div>'+table(head,[metricsrow(t,'../')])
    b+=f'<p class="meta">价格来源：10/23常规时段Longbridge报价。10/23最高 {f(m["high"])}、最低 {f(m["low"])}、成交额 {f(m["turnover_friday_dollars"]/1e9)}十亿美元。高低点只供周一参考，之后每天换成最新完整交易日。</p>'
    if t in NEW:
        s=NEW[t];ev=s['next_week_event']
        b+=section('facts','最新已读披露与现金质量',f'<p><b>期间：</b>{E(s["fiscal_period"])} · <b>业务路径：</b>{E(s["pathway"])}</p>'+factlist(s,'../')+f'<p><b>公司指引：</b>{cleanparagraph(s["guidance"],"../")}</p><p><b>现金质量：</b>{cleanparagraph(s["cash_quality"],"../")}</p>')
        b+=section('thesis','反弹逻辑与反例',f'<p><b>可能的预期差（研究判断）：</b>{cleanparagraph(s["rebound_case"],"../")}</p><p><b>最强反例：</b>{cleanparagraph(s["trap_case"],"../")}</p><p><b>否决：</b>{cleanparagraph(s["kill"],"../")}</p><p><b>重新入选：</b>{cleanparagraph(s["trigger"],"../")}</p><p>这里没有完整正常化盈利预测、目标价或已验证市场一致预期修正；修复逻辑仍须经过价格与实际披露检验。</p>')
        b+=section('event','事件与估值边界',f'<p><b>事件状态：</b>{E(text(ev.get("status")))}；日期 {E(text(ev.get("date_et")) or "未核实")}；时间 {E(text(ev.get("time_et")) or "未核实")}。{E(text(ev.get("note")))}</p>'+refs(s['source_ids'],'../')+f'<p>供应商TTM P/E：{f(m["pe_ttm"]) if m["pe_ttm"] is not None and m["pe_ttm"]>0 else "NM"}。这是GAAP历史分母快照，未完成所有公司一次性收益、SBC、并购及调整后指引的逐项重估；不能据此宣布便宜或推导目标价。</p>')
    else:
        s=OLD[t]
        oldrefs=['OLD-'+str(x['id']) for x in json.loads((P.parent/'2026-10-24/source_register.json').read_text(encoding='utf-8')) if x['ticker']==t]
        b+=section('facts','保留的完整研究逻辑','<p>以下保留前稿已读披露；精确财务期间与完整来源见原个股页。当前价格与上表更新日一致，原估值时间戳保持原样，不混写成新估值。</p><ul>'+''.join('<li>'+E(x)+'</li>' for x in s['facts'])+'</ul>'+refs(oldrefs,'../')+f'<p><b>现金质量：</b>{E(s["quality"])}</p>')
        b+=section('thesis','持有依据、否决与后续证据',f'<p><b>原论点：</b>{E(s["case"])}</p><p><b>反面情景：</b>{E(s["bear"])}</p><p><b>否决：</b>{E(s["kill"])}</p><p><b>再验证：</b>{E(s["proof"])}</p><p><a href="../../2026-10-24/stocks/{safe(t)}.html">查看原详细个股页及当时估值 →</a></p>')
        this=[e for e in events if e['ticker']==t]
        b+=section('event','本周事件',table(['日期ET','事件','发布窗口','电话会ET','证据'],[[e['date_et'],E(e['title']),E(e['release_window']),e['call_time_et'],ref(e['source_id'],'../')] for e in this]) if this else '<p>本轮没有新增核实的下周确定公司财报时点；以原研究与动态公告为准，不能将未核实当作保证无事件。</p>')
    occurs=[d for d in A['days'] if t in d['names']]
    b+=section('days','五天中的研究安排',('<ul>'+''.join(f'<li><a href="../days/day_{d["date"].replace("-","")}.html">{d["date"]} {d["label"]}</a>：{E(d["theme"])}。{E(d["rule"])}</li>' for d in occurs)+'</ul>') if occurs else '<p>保留在55股研究池，未进入本周12股/日的优先队列；不意味着应在其余日期交易。出现新的公司事实后再排序。</p>')
    b+='<p><b>仓位边界：</b>入选前先核WLS；反弹研究试仓示例0.5%，确认后最多1%，合并反弹预算最多4%、共同科技风险最多8%；全部包含在原20%首批/50%条件总股票预算内。未通过则0。</p>'
    (P/'stocks'/f'{safe(t)}.html').write_text(page(title,b,'../'),encoding='utf-8')

(P/'days').mkdir(exist_ok=True)
for d in A['days']:
    b=f'<p class="lede">{E(d["theme"])}</p><div class="notice warning"><b>事前预选，尚待当日刷新：</b>本页在10月25日制作，使用10/23常规时段数据。{E(d["date"])}的实际价格、业绩结果和信号尚未发生；未来数据栏不填造值。</div><p>{common_notice}</p>'
    b+=section('decision','当天筛选动作',f'<p>{E(d["rule"])}</p><p><b>先研究：</b>'+ ' / '.join(d['focus'])+'。<b>事件前或结果未核实等待：</b>'+' / '.join(d['wait'])+'。</p>'+table(['当日必须补齐的输入','目前状态'],[['前一交易日完整收盘、最高/最低与同口径成交量','待当日更新；不能整周沿用10/23锚点'],['前一晚/盘前已发生的公司披露及指引变化','待事件发生后实读；不预设超预期'],['美债收益率、油价与QQQ/SMH相对走势','待当日核对；无法取得可比数据则不扩仓'],['WLS资格、当前总持仓、现金与未成交订单','待账户/终端资料；不可直接生成订单']]))
    b+=section('candidates','12只当日研究对象（历史参考价格）',table(head,[metricsrow(t,'../') for t in d['names']]))
    for t in d['names']:
        role='优先复核' if t in d['focus'] else '事件等待' if t in d['wait'] else '条件观察'
        m=M[t]
        b+=f'<article id="{safe(t)}"><h3>{stocklink(t,"../")} · {E(m["name"])} <span class="badge">{role}</span></h3>'+stocksummary(t,'../')
        if t in NEW:
            s=NEW[t]
            b+=f'<p><b>当天需要的新增证据：</b>{cleanparagraph(s["trigger"],"../")}</p><p><b>事件提醒：</b>{E(text(s["next_week_event"].get("note")))}</p>'+refs(s['source_ids'],'../')
        else:b+=f'<p><b>当天需要的新增证据：</b>{E(OLD[t]["proof"])}</p>'
        b+=f'<p><b>价格条件：</b>最新完整交易日高低点需当天重取。10/23历史参考高 {f(m["high"])}、低 {f(m["low"])}，不是固定下单价。若当前日低点继续下降或相对QQQ/SMH仍走弱，不为完成名单建仓。</p><p><a href="../stocks/{safe(t)}.html">完整事实、现金质量、反方与估值限制 →</a></p></article>'
    dayevents=[e for e in events if e['date_et']==d['date']]
    b+=section('calendar','当日已登记事件',table(['事件','首次发布','电话会/数据ET','北京时间','证据'],[[E(e['ticker']+' '+e['title']),E(e['release_window']),e['call_time_et'],e['beijing_call'],ref(e['source_id'],'../')] for e in dayevents]) if dayevents else '<p>本研究已核实的候选事件登记中，当日没有确定时点；这不表示市场无公告或无宏观消息。</p>')
    b+=section('risk','日内升级与取消规则','<p>先验WLS与现金预算，再读实际披露；至少开盘观察30分钟，确认价差与相对表现。事件未过、下调指引未解释、跳空高开超过3%或触发后跌破最新完整日低点时，取消该次新仓候选。试仓总计最多2%且占用原预算；当日没有通过者，保留现金也是完整结果。</p><p>收盘记录：真实候选状态、实际净值与回撤、尚未成交订单、次日事件和同类总风险。当天“研究优先”不得直接写成“已成交”或“推荐买满”。</p>')
    (P/'days'/f'day_{d["date"].replace("-","")}.html').write_text(page(d['label']+' '+d['date']+' 个股预选报告',b,'../',subtitle='编制日2026-10-25 · 该交易日尚未发生 · 行情参考10/23'),encoding='utf-8')

ledger='<p class="lede">事实与管理判断分开。以下来源可支持对应披露和日期；缺失、索引或转载证据均保留其边界。</p>'
for s in A['sources']:
    ledger+=f'<article id="{E(s["id"])}" class="source"><h3>{E(s["id"])}</h3><p><a href="{E(s["url"])}">{E(s["title"])}</a></p><p class="meta">来源：{E(s.get("source_type",""))} · 发布：{E(s.get("published",""))} · 查阅：{E(s.get("accessed",""))}</p>'+(f'<p>{E(text(s["facts"]))}</p>' if 'facts'in s else '')+'</article>'
(P/'sources.html').write_text(page('来源登记与证据边界',ledger),encoding='utf-8')
print('Built 55 stock pages,5 daily previews,1 overview,1 source ledger;18 event rows.')
