from pathlib import Path
import json, html, math
P=Path(__file__).resolve().parent
A=json.loads((P/'analysis_close.json').read_text(encoding='utf-8'))
S=json.loads((P.parent/'stock_research_synthesis.json').read_text(encoding='utf-8'))['stocks']
M=A['metrics']; R=A['risk']; W=A['models']; E=lambda x:html.escape(str(x),quote=True)
order=list(S)
names={'原B_75':'原B · 75%股票','原B同比缩到50':'原B同比降至50%','修订B_50':'条件目标 · 50%','修订B周一20':'首批上限 · 20%','修订B条件35':'确认阶段 · 35%'}
def f(x,n=2):return f'{x:,.{n}f}'
def pct(x):return f'{x:+.2f}%'
def table(head,rows):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+str(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def link(t):return '../stocks/'+t.replace('.','_')+'.html'
def section(id,title,body):return f'<section id="{id}"><h2>{title}</h2>{body}</section>'
urls={x['id']:x.get('url','') for x in A['source_notes']}
market_note='公开Bloomberg市场综述（SWI转载）显示：纽约16:00美国10年期收益率约5.00%、当日上升5bp；WTI快照约103.63美元、上涨4.2%。这是新闻时点数据，并非本报告独立核验的期货结算价。'
body=f'''<header><div class="eyebrow">BLOOMBERG TRADING CHALLENGE · 2026.10.26 周一准备</div><h1>保留现金，等待事件验证<br>再把股票仓位从20%推进至50%</h1><p class="lede">周五收盘更新与15只个股复核。当前更适合用小仓位获取观察权，把新增风险预算留给美联储、通胀数据与集中财报后的证据。</p><p class="meta">行情日：2026-10-23 美股常规时段收盘 · 采集：{E(A['captured_utc'])} · 研究日：2026-10-24 · 条件性比赛账户研究</p></header>
<nav><a href="#decision">仓位选择</a><a href="#market">全球市场</a><a href="#allocation">周一配置</a><a href="#stocks">逐股复核</a><a href="#risk">风险计算</a><a href="#events">事件日历</a><a href="#execution">执行条件</a><a href="#evidence">证据与限制</a></nav>
<div class="notice"><b>本轮更新：</b>用户已确认允许50%或80%现金；首次建仓已完成，目前持有防守资产。以下按全部购买力可重新配置规划，百分比均为组合总净值。实际持仓、账户净值、WLS当日成员资格仍未取得；因此这是条件性仓位方案，尚不能直接生成可执行订单。</div>'''
body+=section('decision','先确定风险预算，再选择推进速度', '''<p><b>主方案：周一先以20%股票为上限；35%作为确认后的过渡；50%作为证据充分时的条件目标。</b>这三档沿用同一组研究对象，避免临时加入新题材。50%是本轮配置上限，不是必须买满的任务。原75%股票B方案只用于风险对照。</p>'''+table(['方案','股票 / 现金','适用条件','主要代价'],[
 ['观察型（推荐起步）','20% / 80%','周一资格、报价与持仓核对后，最多先完成一半首批；风险条件不合格可继续持币','市场快速反弹时参与度低'],
 ['确认型','35% / 65%','美联储与10/29数据消化，且10/30主要财报核验后；以50%目标各股票权重×0.7计算','仍受选股及防守风格拖累'],
 ['目标型','50% / 50%','市场宽度改善、收益率和油价不再恶化，逐股现金流/指引通过复核；分数日推进','衰退压力情景仍约亏9.32%'],
 ['原B（对照）','75% / 25%','本轮不作为起步方案','同一衰退假设约亏14.70%，超过12%容忍度']])+'''<p>目标超额收益来自对现金流质量与事件风险的筛选，以及保留购买力等待结果；本轮没有估计可靠的预期收益、事件概率或WLS主动权重，因此不声称数学最优或保证比赛排名。若所有股票同步上涨10%，仅持仓比例就使20%与50%股票组合约贡献2%与5%，未计现金收益；与满仓同幅上涨组合相比，会落后约8与5个百分点。</p>''')

sectors={'XLK':'科技','XLF':'金融','XLV':'医疗','XLE':'能源','XLI':'工业','XLP':'必需消费','XLY':'可选消费','XLU':'公用事业','XLB':'材料','XLRE':'地产','XLC':'通信'}
bars=''
for s in sorted(sectors,key=lambda s:M[s]['quote_r1'],reverse=True):
    x=M[s]['quote_r1']; width=abs(x)/3*36
    bars+=f'<div class="barrow"><span>{sectors[s]} <small>{s}</small></span><div class="track"><i style="left:{50 if x>=0 else 50-width}%;width:{width}%;background:{"#008975" if x>=0 else "#c94739"}"></i></div><strong>{pct(x)}</strong></div>'
marketrows=[[s,label,f(M[s]['close']),pct(M[s]['quote_r1']),pct(M[s]['r5']),pct(M[s]['r21'])] for s,label in [('SPY','美股大盘'),('RSP','美股等权'),('QQQ','纳斯达克100'),('IWM','小盘'),('ACWI','全球股票'),('VGK','欧洲'),('EWJ','日本'),('EEM','新兴市场'),('FXI','中国大盘'),('INDA','印度'),('EWY','韩国'),('EWZ','巴西'),('SMH','半导体'),('GLD','黄金'),('TLT','长债'),('UUP','美元'),('USO','石油期货基金')]]
body+=section('market','全球市场：冲击仍在，板块表现分化',f'<p>{market_note} <a href="{urls["M1"]}">Bloomberg综述来源</a></p><p>价格代理显示：SPY {pct(M["SPY"]["quote_r1"])}、RSP {pct(M["RSP"]["quote_r1"])}，QQQ {pct(M["QQQ"]["quote_r1"])}；11个行业ETF仅{A["sector_proxy_up_count"]}个上涨。能源与科技相对强，必需消费并未提供当日保护。此处是<b>行业代理宽度</b>，不是交易所全市场涨跌家数或成分股广度。</p><div class="chart"><h3>周五11行业代理涨跌</h3>{bars}<p class="meta">数据：Longbridge常规时段报价；百分比相对报价接口prev_close。</p></div>'+table(['代理','观察范围','收盘美元','周五','5日','21日'],marketrows)+'''<p>这些ETF仅用于研究，不能纳入本次交易清单。国家ETF是美股时段、美元计价的包装工具，混合了当地股市、汇率、时区差及跟踪误差；不能把它们等同于当地指数同日收盘。USO受期货曲线与展期影响，也不是现货WTI价格。</p>'''+table(['传导路径','对候选股的影响','仓位含义'],[
 ['油价上行 → 通胀与融资成本','XOM/CVX受益可能被需求、税费、成本和价差变化抵销；PG/WMT面临成本及估值压力','能源合计首批3%、目标8%；不把能源当保险'],
 ['收益率上行 → 高估值压缩','MSFT/GOOGL现金投入大；WMT指引估值高；NEE资本需求大','财报前科技首批0；WMT上限3%；NEE继续观察'],
 ['风险偏好转弱 → 防守拥挤松动','JNJ/PG也可能下跌；LMT订单强但近期涨幅大','防守股要看价格和现金，不因标签而补仓'],
 ['海外增长与汇率','TM受日元与汽车周期影响；TSM/NVDA是原始研究对照、非本轮15只配置','TM不入目标；跨市场价格仅辅助判断'],
 ['停火、油价回落 → 风格反转','能源/LMT可能下跌，同时科技与全球股票上涨','接受防守组合可能跑输；不能把反向相关长期化']]))

alloc=[]
for t in order:
    alloc.append([f'<a href="#stock-{t.replace(".","_")}">{t}</a>',S[t]['name'],f(W['修订B周一20'][t]),f(W['修订B条件35'][t]),f(W['修订B_50'][t]),f(M[t]['close']),pct(M[t]['quote_r1'])])
alloc.append(['CASH','现金','80.00','65.00','50.00','—','—'])
body+=section('allocation','具体仓位：按组合总净值计算',table(['股票','名称','首批上限%','确认阶段%','条件目标%','周五收盘$','周五涨跌'],alloc)+'''<p>当前防守资产没有逐项明细，表格表示<b>完成调整后的总持仓</b>，不能在现有资产上再额外叠加。先计算“目标持仓金额−当前持仓市值−未成交买单金额”，再确定新增金额；卖出资产是否释放可用购买力，以比赛终端规则为准。已持有但不在表中的股票也占净值、行业和现金预算。</p><p>AMZN、ETN、TM、NEE的目标为0：保留研究和重新进入条件，不以低配解读为必须补齐。单名20%是用户限制；本方案最大的单名目标7%，主动留出跳空和模型误差余量。确认型与目标型都是条件上限，不能仅因价格上涨就自动提高仓位。</p>''')

valuation={
 'JNJ':('FY26调整后EPS中值',11.10,'公司调整后指引；诉讼和下一年并购稀释另计'),
 'ABBV':('FY26调整后EPS中值',13.86,'使用10/5修订指引13.76–13.96，非旧版指引'),
 'PG':('FY27核心EPS中值',7.00,'全年指引6.89–7.11；核心口径非GAAP'),
 'WMT':('FY27调整后EPS中值',2.835,'全年指引2.80–2.87；高倍数有压缩风险'),
 'LMT':('FY26EPS指引中值',30.55,'全年30.35–30.75；现金流仍须看合同资产'),
 'ETN':('FY26调整后EPS中值',13.50,'全年13.40–13.60；GAAP指引明显更低'),
 'NEE':('FY26调整后EPS中值',3.97,'全年3.92–4.02；非现金对冲不代表可分配现金')}
actions={
 'XOM':'保留首批2%、目标5%。周五涨2.79%后不追高；和CVX同看10/30现金流、营运资本和炼化因素桥。油价上涨不是无条件加仓理由。',
 'CVX':'保留首批1%、目标3%。与XOM合并管理：首批3%、目标8%；并表与营运资本释放需要剔除，不能把两家公司当两种独立保护。',
 'JNJ':'保留首批3%、目标5%。周五回落不等于估值有安全边际；调整后EPS掩盖的法律成本和2027并购稀释仍须计入经济价值。',
 'ABBV':'首批0、目标3%，等待10/30财报。新指引已含IPR&D影响，重点看Skyrizi/Rinvoq持续性与股息后的现金余量。',
 'PG':'首批3%、目标7%只是上限。周五下跌约2.12%，且在目标组合的样本风险贡献最大；若周一继续显著弱于XLP并伴随指引变化，暂停第二批，先核查有机量价与利润率。',
 'WMT':'首批2%、目标3%。现金流质量尚可，但指引倍数高；下跌1%并未消除估值风险，11/19财报又在比赛结束之后。',
 'JPM':'首批4%、目标6%。Q3拨备是增加而非释放；信用成本、费用增长与高有形账面倍数是约束。金融与BRK合计首批7%、目标12%，避免被现金稀释后的低总波动误导。',
 'BRK.B':'首批3%、目标6%。保险浮存金及现金有弹性，但投资收益与外汇变化影响利润；账面倍数仅供粗定位，不能把集团现金全部视作可分配现金。',
 'MSFT':'首批0、目标5%，待10/28盘后财报。Azure增长必须与现金资本开支、融资租赁及真实FCF改善并看；先等结果，再看市场如何定价。',
 'GOOGL':'首批0、目标3%，待10/28结果。未正常化的GAAP EPS含巨额投资估值收益，低TTM P/E不构成便宜证据；重点看核心经营利润与资本开支后的现金。',
 'AMZN':'首批及目标均0。Anthropic投资收益与运营现金改善分开；TTM CFO减PPE为负，债务及租赁需求高。10/29财报确认前不通过替代买入扩大科技预算。',
 'LMT':'首批2%、目标4%只是上限。10日涨幅约18.56%，周五又涨2.42%；不因订单增长而追价。固定价格合同、合同资产与并购现金支出会影响兑现。',
 'ETN':'首批及目标均0。订单与数据中心需求强，但收购使负债上升，利润率与现金需验证；11/3财报后如重新入选，必须替换现有预算。',
 'TM':'首批及目标均0。净利润大幅增长包含金融与汇率因素，营业利润同比下降；日元敏感性与ADR/WLS资格尚未完成核验。',
 'NEE':'首批及目标均0。公用事业标签不消除利率风险；经营现金流与增长投入缺口、融资和非现金对冲仍是主约束。'}
cards=''
for t in order:
    m=M[t]; note=S[t]
    if t in valuation:
        label,den,lim=valuation[t]; val=f'{label} {f(den,3)}美元，按周五收盘计算约 <b>{f(m["close"]/den)}倍</b>。{lim}。不是跨公司统一可比口径，也不是目标价。'
    elif t=='JPM':val=f'Q3每股有形账面112.64美元，周五股价约为其 <b>{f(m["close"]/112.64)}倍</b>；高回报率维持与信用成本是估值能否持续的关键。'
    elif t=='BRK.B':val=f'Q2 B类每股账面约348.26美元，周五约 <b>{f(m["close"]/348.26)}倍</b>；不是重估后的资产净值，也不能直接推出合理价。'
    else:val='本轮不建立缺乏可审计正常化利润支持的目标价；沿用完整个股页对周期利润、投资收益、资本开支与汇率的拆分。'
    cards+=f'''<article class="stock" id="stock-{t.replace('.', '_')}"><h3>{t} · {E(note['name'])}</h3><p class="meta">收盘 ${f(m['close'])} · 周五 {pct(m['quote_r1'])} · 5日 {pct(m['r5'])} · 21日 {pct(m['r21'])} · 20日均线 ${f(m['ma20'])} · 60日年化波动 {f(m['vol60'])}%</p><p><b>仓位判断：</b>{E(actions[t])}</p><p><b>重新定价：</b>{val}</p><p><b>盈利与现金质量：</b>{E(note['quality'])}</p><p><b>反证与退出依据：</b>{E(note['kill'])}</p><p><a href="{link(t)}">查看完整个股事实、财务拆分、反面情景与原始来源 →</a></p></article>'''
body+=section('stocks','15只个股：价格更新，研究结论逐项复核','<p>下面在已有逐股研究上更新价格、估值和行动。既有公司财务事实的披露期与来源沿用完整个股页，本次没有假设出现新一期财报。股价变化不自动构成基本面改善或恶化。</p>'+cards)

riskrows=[]
for n in ['原B_75','原B同比缩到50','修订B_50','修订B条件35','修订B周一20']:
    r=R[n]
    riskrows.append([names[n],f(r['windows']['20']['vol']),f(r['windows']['60']['vol']),f(r['windows']['120']['vol']),f(r['windows']['252']['vol']),f(r['windows']['60']['correlation_shift_vol']),f(r['windows']['60']['all_positive_one_vol'])])
stressrows=[]
for scenario in A['stress_vectors']:
    stressrows.append([scenario,*[pct(R[n]['scenario'][scenario]) for n in ['原B_75','原B同比缩到50','修订B_50','修订B条件35','修订B周一20']]])
vc=sorted(R['修订B_50']['variance_contributions'].items(),key=lambda x:x[1],reverse=True)
body+=section('risk','风险复核：样本分散不能替代现金缓冲',table(['组合','20日波动%','60日%','120日%','252日%','相关性上移60日%','全同向60日%'],riskrows)+'''<p>表内均为<b>年化标准差</b>，不是最大亏损、下周跌幅预测或风险价值VaR。相关性上移用0.5×样本相关矩阵+0.5×全1矩阵，固定各股波动；全同向设相关性为+1。两者只检验分散失效，不含波动率本身进一步上升、流动性冲击和跳空。</p>'''+table(['主观压力假设','原B75%','原B降到50%','修订50%','确认35%','首批20%'],stressrows)+'''<p><b>压力假设没有概率，也不是亏损边界。</b>相同衰退假设下，原B损失14.70%，降到50%后为9.80%，改换成分后为9.32%：改善5.38个百分点中，4.90来自降低股票敞口，只有0.48来自成分调整。修订50%的样本波动还高于原B同比降到50%，不能宣称它在所有风险指标上更优。</p><p>12%是用户容忍度。9.32%的情景损失距离12%仅2.68个百分点；不应把这个差额视作可自由花掉的余量，也不能按12÷9.32把仓位机械提高到64.4%。上述冲击可能低估真实尾部风险。</p>'''+table(['目标组合股票','60日方差贡献%','总净值权重%','单名主观冲击%','对应净值损失%'],[[t,f(v),f(W['修订B_50'][t]),f(A['individual_shock_assumptions'][t]*100),f(R['修订B_50']['single_name_scenario_losses'][t])] for t,v in vc])+'''<p>PG、JNJ、WMT合计约41.88%的样本方差；金融/综合组12%总净值占50%股票部分的24%，首批JPM+BRK7%占20%股票部分的35%。能源8%、医疗8%、必需消费10%、金融/综合12%、科技8%、国防4%是相关风险桶，不应当成六种相互独立的资产。</p><p>目标组合60日SPY回归beta约为'''+f(R['修订B_50']['beta_proxy']['SPY'],3)+'''，ACWI代理beta约为'''+f(R['修订B_50']['beta_proxy']['ACWI'],3)+'''。这来自特定样本的价格共同变化，不代表净股票敞口为零，更不代表在下跌时可靠对冲；总多头和净股票敞口仍均为50%。WLS基准序列缺失，无法给出真实WLS beta、主动权重或跟踪误差。</p><p>单名极端敏感性：若JPM下跌30%，6%目标约损失1.80%净值；能源合计8%同时跌25%，约损失2.00%。若额外采用“单股主观压力损失≤1.5%净值”纪律，则JPM在-30%假设下应≤5%，差额留现金。本轮将其作为更保守替代分支，不声称用户已接受该新增硬约束。</p>''')

body+=section('events','下周时间表：先处理宏观，再处理集中财报',table(['事件','纽约时间','北京时间','仓位动作'],[
 ['周一10/26美股常规交易','09:30–16:00 ET','10/26 21:30–10/27 04:00','先核对资格与实际持仓；首批上限20%，可只买一半或继续持币'],
 [f'<a href="{urls["E1"]}">FOMC会议 / 决议</a>','10/27–28；10/28 14:00','10/29 02:00；发布会02:30','不在会议前把股票提高到50%；关注利率路径与通胀表述'],
 ['MSFT / GOOGL财报','10/28盘后；具体发布时间再核对','10/29凌晨','先核实现金资本开支、经营增长和指引，再考虑科技预算；GOOGL日期证据为公司公告转载，非直接IR全文'],
 [f'<a href="{urls["E2"]}">GDP初值 + 9月个人收入支出/PCE</a>','10/29 08:30','10/29 20:30','同时看增长和价格，不能把强增长单向解读为利好'],
 ['AMZN财报','10/29盘后','10/30凌晨','仍以观察为主，不因盘后上涨自动恢复仓位'],
 ['XOM / CVX / ABBV集中财报','10/30；XOM05:30 CT披露，08:30 CT电话会；CVX11:00 ET电话会；ABBV盘前','XOM18:30/21:30；CVX23:00；ABBV具体时点核对','周五前能源与ABBV不得直接跳到目标；核实现金质量后再推进35%或50%'],
 ['ETN财报','11/3盘前','11/3晚间','只有现金、负债和指引通过，才讨论替换已有预算'],
 ['BRK / TM下一期','具体日期本轮未直接确认','待核验','不能编入已确认的精确下单日历']])+'''<p>本周美国仍使用夏令时，北京比纽约快12小时。11/1以后美国切换标准时，后续事件必须重新换算。公司事件沿用已有来源登记，宏观日期本次重新查验官方日历；终端日历如有更新，以实际公告为准。比赛结束日按已有研究11/13规划，WMT11/19和JNJ12/8事件不算窗口内催化。</p>''')

body+=section('execution','周一执行条件与回撤纪律', '''<ol><li><b>盘前：</b>核对WLS当日成员、普通股交易资格、总净值、现有资产与未成交订单。未核实的股票留现金，不用同板块股票临时替代。用户已确认可保留50%或80%现金；该信息来源是用户，不是本轮独立取得的比赛手册。</li><li><b>开盘后先观察30分钟：</b>用实时买卖价及成交量确认流动性。若买卖价差超过0.20%、报价停滞、停牌或缺乏足够成交，不执行该批。价差门槛是本报告管理假设，未做收益回测。</li><li><b>首批分两段：</b>表内20%首批的每只股票先做一半，合计10%；第二段另10%须在价格稳定、无新利空、组合预算仍合格时才考虑，未满足就留现金。任何一只股票未成交，不把其额度转移给其他名字。</li><li><b>能源与LMT不追涨：</b>周一若较周五收盘高开超过2%，暂缓该股，重新核价；XOM参考约186.87美元、CVX237.87、LMT616.26。此门槛仅是避免追涨的执行纪律，不是估值上限、止损或买入承诺。</li><li><b>下跌也不盲目接：</b>若候选股较周五跌超过3%，先判断业绩/政策/法律消息是否改变论点，再决定是否保持原首批；不依据“已跌很多”自动加倍。不能用止损单保证跳空时的成交价。</li><li><b>宏观冻结条件：</b>若最新可核验的10年期收益率较周五约5.00%再上升10bp以上，或WTI同口径快照上涨超过5%，暂缓新增风险并重做估值。若无法取得可比报价，同样先不扩仓。阈值是主观管理规则，不是已验证择时模型。</li><li><b>提高仓位：</b>35%与50%只在相应事件和逐股质量验证后推进；科技、ABBV、能源各自要通过财报检验。价格突破20日均线可以作为价格确认之一，但不足以替代现金流和指引复核。</li></ol>'''+table(['自本轮风险管理基准净值高点回撤','对应动作（条件规则）'],[
 ['4%','停止新增，逐股复核主因；保留未使用现金'],['6%','重新压力测试；建议股票敞口降至不高于35%，若已更低则不反向加仓'],['8%','建议股票敞口不高于20%；优先移除论点失效与集中事件风险'],['10%','以最低风险为目标，必要时现金接近90%；先核对比赛实际限制与可成交性'],['12%','已触及用户风险容忍预算；视为方案失效，重建研究与风险假设，不能承诺能精确停在12%']])+'''<p>净值必须包括全部持仓和现金，扣除费用，并剔除入出金造成的机械变化；基准高点及比赛系统的实际回撤定义应记录。阈值在盘中跳空和流动性受限时可能被越过，风险控制无法保证绝对损失上限。</p><h3>流动性与数量换算</h3><p>20日“收盘价×成交量”的均值仅是美元成交额代理，不是逐笔真实成交额。以单日参与率5%作保守检查：退出天数≈持仓市值÷（20日美元成交额代理×5%）。未提供账户净值，不能断言所有规模都可迅速退出。以下工具仅估算目标持仓与流动性，不发单。</p><div class="calc"><label>组合净值（美元）<input id="nav" type="number" min="1" value="1000000"></label><label>阶段<select id="stage"><option value="修订B周一20">首批20%</option><option value="修订B条件35">确认35%</option><option value="修订B_50">目标50%</option></select></label><button id="recalc">计算参考数量</button><div id="calc-result" aria-live="polite"></div></div>''')

body+=section('evidence','数据与证据：本轮确认了什么，仍缺什么',table(['事项','处理与边界'],[
 ['周五完整常规时段','48个报价last_done，时间戳20:00:00/01 UTC；明确排除post_market，不能视为周一可成交价格'],
 ['历史拼接','保留截至10/22的259个已存收盘，新增10/23常规时段报价，得到260个价格、259个收益；日历史接口权限拒绝301607，未独立用该接口验证收盘bar'],
 ['唯一前收盘不一致','PG旧历史164.497，最新prev_close164.502，差0.005美元（约0.304bp）。不改原始历史；日涨跌采用报价prev_close，风险采用旧历史拼接。替换该前收盘时，目标60日年化波动仅改变约'+f(A['PG_vol_sensitivity_pp'],6)+'个百分点'],
 ['基本面','沿用15只完整个股研究和43条一手来源登记；各公司GAAP/调整后、公司FCF/分析师CFO减PPE、季度/全年不混算'],
 ['规则','已完成首次建仓、全购买力重配、允许50%/80%现金为用户确认；WLS当日资格和真实持仓尚缺'],
 ['可得与缺失','有价格、成交量代理、部分财务和公司指引；缺当前WLS成员和基准序列、账户净值和仓位、可复核完整前瞻估值、可靠事件概率、周一实时点差'],
 ['收益及风险','加权对数收益协方差近似，现金收益0；不含费用、税、滑点、融资及完整总收益复权核验。不将构建后组合套用历史的一日表现当作真实业绩或样本外验证']])+'''<p>下列结构化文件允许复核来源、输入和计算；旧报告保留原时间戳，避免把旧盘中数字伪装成新收盘数据。周五收盘后尚未发生的周末新闻不在本轮证据中，周一仍需盘前检查。</p>'''+table(['来源/文件','用途'],[
 ['<a href="closing_quotes.json">常规时段报价原始快照</a>','包含独立的post_market字段；计算未使用盘后价格'],
 ['<a href="analysis_close.json">完整风险与价格计算</a> / <a href="aligned_prices.csv">对齐价格序列</a>','支持独立算术复核'],
 ['<a href="close_metrics.csv">价格指标</a> / <a href="allocations_close.csv">各档配置</a>','48个市场代理与股票；配置只含正股和现金'],
 ['<a href="source_notes.json">本轮来源登记</a> / <a href="validation_close.json">验证结果</a>','来源时间、限制、计算与页面检查'],
 ['<a href="../source_register.json">原15股一手来源登记</a> / <a href="../stock_deep_dive_risk_20261024.html">完整15股研究</a>','详细事实、反方与重新进入条件'],
 ['<a href="../../2026-10-23/global_market_positioning_20261026.html">原全球市场报告</a>','保留原A/B/C和旧行情时间戳，只作历史对照']])+f'<p>本轮宏观来源：<a href="{urls["M1"]}">Bloomberg市场综述（SWI转载）</a>；<a href="{urls["E1"]}">美联储官方日历</a>；<a href="{urls["E2"]}">BEA官方日历</a>。股票披露的逐条链接位于各股完整页。无交易执行。</p>')
payload=json.dumps({'models':W,'metrics':{t:{'close':M[t]['close'],'adv':M[t]['dollar_volume_proxy20']} for t in order}},ensure_ascii=False).replace('</','<\\/')
script='''<script>const DATA=PAYLOAD;function calc(){const nav=Number(document.querySelector('#nav').value),w=DATA.models[document.querySelector('#stage').value];if(!Number.isFinite(nav)||nav<=0){document.querySelector('#calc-result').textContent='请输入正的组合净值。';return;}let out='<div class="scroll"><table><thead><tr><th>股票</th><th>目标市值$</th><th>参考整数股</th><th>5%参与率退出天数</th></tr></thead><tbody>';for(const[t,m]of Object.entries(DATA.metrics)){if(!w[t])continue;const amount=nav*w[t]/100;out+=`<tr><td>${t}</td><td>${amount.toLocaleString(undefined,{maximumFractionDigits:2})}</td><td>${Math.floor(amount/m.close)}</td><td>${(amount/(m.adv*.05)).toFixed(4)}</td></tr>`;}out+='</tbody></table></div><p>按周五收盘向下取整，仅表示目标持仓参考；未扣现有持仓、未成交订单、费用与滑点。净值过大或成交条件变化时需重新限制规模。</p>';document.querySelector('#calc-result').innerHTML=out;}document.querySelector('#recalc').addEventListener('click',calc);calc();</script>'''.replace('PAYLOAD',payload)
css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f6f7f5;color:#18312f;font:16px/1.8 "Segoe UI","Microsoft YaHei",sans-serif}main{max-width:1200px;margin:auto;padding:40px 38px 90px}header{padding:30px 0 36px;border-bottom:4px solid #137967}h1{font-size:43px;line-height:1.35;letter-spacing:-1px;margin:16px 0 22px}h2{font-size:28px;line-height:1.45;margin:0 0 22px}h3{font-size:21px;margin:12px 0}.eyebrow{font-size:13px;font-weight:700;letter-spacing:2px;color:#16735f}.lede{font-size:19px;max-width:900px}.meta{font-size:13px;color:#647775}nav{display:flex;flex-wrap:wrap;gap:12px 23px;padding:20px 0}a{color:#006d65;text-underline-offset:4px}section{padding:48px 0 30px;border-bottom:1px solid #d7e0dc;scroll-margin-top:25px}p{margin:14px 0 20px}.notice{padding:20px 24px;background:#e8f0eb;border-left:4px solid #16846e;margin:18px 0}.scroll{overflow-x:auto;margin:24px 0}table{border-collapse:collapse;width:100%;font-size:14px;background:white}th{text-align:left;background:#e3ece7;color:#254a40;font-weight:650}th,td{padding:12px 14px;vertical-align:top;border-bottom:1px solid #e4e8e4}tr:nth-child(even) td{background:#fafbf9}.stock{padding:24px 0 28px;border-top:1px solid #d4dfd8;scroll-margin-top:20px}.stock:first-of-type{border-top:0}.chart{padding:24px 28px;background:white;margin:28px 0;border:1px solid #e1e8e3}.barrow{display:grid;grid-template-columns:130px 1fr 75px;gap:14px;align-items:center;height:35px;font-size:14px}.barrow small{color:#6c7a75}.track{position:relative;height:20px;background:linear-gradient(to right,transparent 49.8%,#899e93 50%,transparent 50.2%)}.track i{position:absolute;height:14px;top:3px;border-radius:2px}.barrow strong{text-align:right;font-variant-numeric:tabular-nums}.calc{padding:24px;background:white;border:1px solid #d7e3dc}label{display:inline-block;margin:0 20px 15px 0}input,select,button{display:block;font:inherit;padding:9px;margin-top:7px;border:1px solid #adc6b7;border-radius:3px;background:white}button{background:#126e5c;color:white;cursor:pointer;display:inline-block}ol{padding-left:24px}li{padding:7px 0 13px}footer{padding-top:28px;color:#6b7b72;font-size:13px}@media(max-width:700px){main{padding:18px 18px 50px}h1{font-size:30px}h2{font-size:24px}section{padding-top:34px}th,td{min-width:95px;padding:10px}td:nth-child(2){min-width:120px}.barrow{grid-template-columns:100px 1fr 64px;gap:7px;font-size:12px}.chart{padding:15px}.lede{font-size:17px}}@media print{body{background:white}main{max-width:none;padding:0}nav,.calc{display:none}section{page-break-before:auto}.stock{page-break-inside:avoid}table{font-size:10px}th,td{padding:6px}}'''
doc='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>周五收盘更新 · 周一仓位与15股风险复核</title><style>'+css+'</style></head><body><main>'+body+'<footer>研究判断与管理阈值均可被新证据推翻。所有价格与事件请按标注时间使用；本报告不提供损失保证。</footer></main>'+script+'</body></html>'
(P/'monday_close_update_20261024.html').write_text(doc,encoding='utf-8')
(P/'stock_actions_close.json').write_text(json.dumps(actions,ensure_ascii=False,indent=2),encoding='utf-8')
print('Built close update,',len(doc),'characters; 15 stock updates.')
