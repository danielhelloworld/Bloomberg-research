from pathlib import Path
import json,html,re,datetime
from decimal import Decimal,ROUND_HALF_UP
P=Path(__file__).resolve().parent
A=json.loads((P/'attack_research.json').read_text(encoding='utf-8'))
M=A['metrics'];S=A['stocks'];SRC={s['id']:s for s in A['sources']}
E=lambda x:html.escape(str(x),quote=True)
def txt(x):
    if x is None:return ''
    if isinstance(x,list):return '；'.join(map(txt,x))
    if isinstance(x,dict):return '；'.join(k+'：'+txt(v) for k,v in x.items())
    return str(x).replace('根代理','本次研究')
def f(x):return '—' if x is None else f'{x:,.2f}'
def pct(x):return '—' if x is None else f'{Decimal(str(x)).quantize(Decimal(".01"),rounding=ROUND_HALF_UP):+}%'
def status(x):
    s=txt(x)
    labels={'company_confirmed':'公司已确认','confirmed_issuer':'公司已确认','confirmed_next_week':'公司已确认','already_reported':'已发布','not_confirmed_in_next_week':'下周明确时点未核实','not_confirmed':'未核实','confirmed_outside_week':'已确认，日期在本周以外'}
    return labels.get(s,s)
def safe(t):return t.replace('.','_')
def ref(id,prefix=''):return f'<a class="ref" href="{prefix}sources.html#{E(id)}">{E(id)}</a>' if id in SRC else ''
def refs(ids,prefix=''):return ' '.join(ref(id,prefix) for id in ids)
def prose(x,prefix=''):
    v=E(txt(x))
    for id in sorted(SRC,key=len,reverse=True):
        for l,r in [('[',']'),('【','】')]:v=v.replace(E(l+id+r),ref(id,prefix))
    return v
def table(head,rows,id=None):return '<div class="scroll"><table'+(f' id="{id}"' if id else '')+'><thead><tr>'+''.join('<th>'+str(h)+'</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def sec(id,title,body):return f'<section id="{id}"><h2>{title}</h2>{body}</section>'
def sl(t,prefix=''):return f'<a href="{prefix}stocks/{safe(t)}.html">{t}</a>'
basehtml=(P.parent/'weekly_expanded_20261026_30.html').read_text(encoding='utf-8')
css=re.search(r'<style>(.*?)</style>',basehtml,re.S).group(1)+''' html{scroll-behavior:auto}.model{padding:22px;background:white;border:1px solid #d3e0d5;margin:22px 0}.calc{background:#e5eee7;padding:24px;margin:25px 0}.calc label{display:inline-block;margin:0 20px 15px 0}.calc input{display:block;max-width:180px}.bigresult{font-size:22px;font-weight:650}.bad{color:#ac352c}.groupdesc{max-width:1000px}.formnote{font-size:13px;color:#667a6b}'''
notice='所有权重占总净值。只做多正股，单股上限20%；约12%组合回撤容忍不是保证损失上限。按现有防守资产可全额重配规划，现金比例允许50%/80%。WLS、证券类别及真实账户明细仍须核验；研究候选尚非可直接执行的买单。'
def page(title,body,prefix=''):
    nav=f'<nav><a href="{prefix}aggressive_equity_20261025.html">进攻研究入口</a><a href="{prefix}aggressive_equity_20261025.html#candidates">28股总表</a><a href="{prefix}aggressive_equity_20261025.html#models">三种预算示例</a><a href="{prefix}aggressive_equity_20261025.html#risk">压力计算</a><a href="{prefix}sources.html">原始来源</a><a href="{prefix}../weekly_expanded_20261026_30.html">55股与五天报告</a></nav>'
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+'</title><style>'+css+'</style></head><body><main><header><div class="eyebrow">BLOOMBERG TRADING CHALLENGE · 进攻型股票研究</div><h1>'+E(title)+'</h1><p class="meta">研究截至2026-10-25 · 最新完整常规时段价格为10/23 · 只研究、不下单</p></header>'+nav+body+'<footer>公司事实、供应商行情、分析计算与主观管理假设分别标注。候选数量、成长率及历史跌幅均不保证收益或比赛排名。</footer></main></body></html>'

advanced=['NVDA','AVGO','ANET','MRVL','GEV','STX','ALAB','PLTR']
watch=['AMD','MU','VRT','CRWD','SNOW','CEG','VST','HOOD','COIN','TSLA','WDC','SNDK']
strict=['CRWV','NBIS','ORCL','TEM','HIMS','ASTS','MSTR']
rank={t:'优先深入研究' for t in advanced};rank.update({t:'事件/估值待验证' for t in watch});rank.update({t:'现金/监管约束，严格观察' for t in strict});rank['RKLB']='比赛窗口论点降级'
assert set(rank)==set(S)
comment={
 'NVDA':'算力收入增长已有证据；进攻靠需求与现金兑现，不能把投资收益和应收占用忽略。',
 'AVGO':'定制芯片和互联业务提供增长，现金转换比单纯项目总额更有解释力；客户集中仍是首要风险。',
 'ANET':'网络投入带来收入与利润，但超大客户采购时点可能令增长波动；11/3自身财报前先看云客户证据。',
 'MRVL':'数据中心增长与新产品交付是进攻路径；GAAP差异、SBC及并购摊销要计入。10/6 Investor Day完整材料尚缺，8月指引不能冒充最新预期，需先补核。',
 'GEV':'订单、燃机和电网交付可提供经营杠杆；10/28财报确认之前，不能把积压订单全部资本化成利润。',
 'STX':'近线硬盘需求与产品升级可以提高盈利；10/27盘后先看真实出货、毛利及现金，避免周期顶部估值陷阱。',
 'ALAB':'连接芯片具有高增长弹性，但规模基数、集中客户与税务收益使GAAP利润需要正常化；价格大跌仍可能高估。',
 'PLTR':'商业化增长和经营杠杆可支持进攻，但估值已要求持续高增长；应考察合同转收入、SBC及真实现金。',
 'RKLB':'Neutron首发已推迟至2027，移出本次比赛的该项催化假设；Electron及其他合同另作经营研究，不进入配置示例。',
 'MSTR':'股票回报同时取决于比特币、融资、优先股及资产溢价；缺完整同日资本结构和资产桥，不用TTM P/E或简单币价倍数定价。',
 'CRWV':'收入增长并不自动覆盖GPU和数据中心资本开支；先核合同现金、利息与后续融资，暂不进入默认配置示例。',
 'NBIS':'预付款可能推高经营现金流；需把递延收入、设备投入及融资一起看，不能据单季CFO认定自我供血。'}

body='<p class="lede">28个进攻候选：原55股研究中12只重新定位，加16家新公司；累计覆盖71家独立公司。优先寻找收入、利润和现金能共同兑现的增长，把融资依赖、主题弹性与监管风险单列。</p><div class="notice">'+notice+'</div>'
body+='<div class="funnel">'+''.join(f'<div><b>{n}</b>{label}</div>' for n,label in [(8,'优先深入研究'),(12,'事件/估值待验证'),(7,'严格观察'),(1,'比赛窗口论点降级')])+'</div>'
body+=sec('priority','进攻研究优先级：先看盈利路径，再看弹性',table(['股票','研究判断','升级前应验证'],[[sl(t),E(comment[t]),prose(S[t]['trigger'])] for t in advanced])+'<p><b>新增对象优先：</b>MRVL、GEV、ALAB、STX。GEV与STX先过下周财报；ALAB属于更小仓位、更高估值要求的观察。优先研究不代表已证实低估；本轮没有可靠的完整前瞻估值、预期修正和概率模型，不能据此给出精确目标价或买入胜率。</p>')
descs={
 '盈利与现金兑现':'收益驱动：订单/部署转成收入、毛利和可分配现金。主要反例：资本开支推迟、客户集中、周期顶部利润或预付款使现金高估。分在这一组不代表每家公司现金口径相同或估值便宜。',
 '增长加速与高预期':'收益驱动：新产品与商业化使增长超过当下可验证框架。主要反例：增长虽高却不及市场要求，SBC与估值压缩吞掉业绩增量。MU还必须按存储周期正常化利润。',
 '资本开支与融资约束':'收益驱动：重资产投入转成持续经营现金。主要反例：订单大、收入快，但融资与利息需求更快；预付款不是已经赚到的利润。',
 '高弹性主题与市场交易':'收益驱动：交易活跃、商业里程碑或风险偏好修复。主要反例：价格已反映远期愿景，监管、资产价格、延迟与股权稀释使股东回报落空。COIN/HOOD/MSTR不是三种独立风险。',
 '医疗商业化与监管':'收益驱动：商业收入、客户留存与单位经济改善。主要反例：投资收益、亏损、SBC、获客与监管依赖；不把AI或减重概念直接当现金回报。'}
for i,(g,names) in enumerate(A['groups'].items()):
    body+=sec('path-'+str(i),g,'<p class="groupdesc">'+E(descs[g])+'</p>'+table(['候选','研究状态','主要经营证据','第一否决'],[[sl(t),E(rank[t]),E(txt(S[t]['facts'][0]['claim']))+' '+ref(S[t]['facts'][0]['source_id']),E(txt(S[t]['kill']))] for t in names]))

ordered=advanced+watch+strict+['RKLB']
rows=[]
for t in ordered:
    m=M[t];pe=m.get('pe_ttm')
    rows.append([sl(t),E(m['name']),E(rank[t]),f(m['close']),pct(m['r5']),pct(m['r10']),pct(m['r_halfyear']),f(pe) if pe is not None and pe>0 else 'NM',f(m['turnover_friday_dollars']/1e9)])
body+=sec('candidates','28股价格与估值快照','<p class="meta">新16股来源data/snapshot_0/1/2.json；旧12股沿用../expanded_research.json。常规时段报价10/23 20:00:00/01 UTC；5/10日、半年为供应商指标，精确窗口端点未独立给出。最后一列是周五实际成交额，不是20日ADV。</p>'+table(['股票','名称','研究状态','收盘$','5日','10日','半年','GAAP TTM P/E','周五成交额$bn'],rows)+'<p>NM表示非正的GAAP盈利分母，不能解读成负倍数很便宜。NBIS、TSLA等极高TTM倍数也不能直接等同前瞻估值；税项、投资收益、金融资产公允价值、SBC和摊销都可能改变分母。WDC拆分后数据、SNDK周期现金口径与不同财年不能混算。本轮不计算缺少数据支持的RSI、ATR、历史beta或回测。</p>')

modelrows=[]
for name,m in A['models'].items():
    modelrows.append([E(name),' / '.join(t+' '+f(w)+'%' for t,w in m['attack'].items()),f(m['attack_pct'])+'%',f(m['cash_pct'])+'%',f(m['total_equity_pct'])+'%'])
body+=sec('models','三种互斥预算示例：选一种逻辑，不叠加','<p>以下是证据全部通过后的研究性配置示例，<b>不是周一必须完成的仓位</b>。共同保留原参考核心42%总净值（移出原MSFT5%和GOOGL3%的8%预算），以进攻部分替换；现有资产未给明细，无法生成实际买卖差额。</p>'+table(['示例','进攻部分：总净值权重','进攻合计','现金','总股票'],modelrows)+'<p><b>主研究方向：</b>先从“盈利兑现型”挑选已通过证据的名字；GEV、STX分别等10/28、10/27实际结果。高增长验证型含ALAB/PLTR等估值敏感名字，容错更小。高风险主题观察型即使举例2%，也需HOOD/COIN财报及TSLA/ASTS各自证据合格，未通过部分保留现金。</p><p>RKLB、MSTR、CRWV、NBIS、TEM、HIMS本轮未进入示例配置。RKLB的2027首发时间不能压缩成2026催化；MSTR缺完整同日资本结构桥；其余公司现金、融资或监管仍有关键缺口。它们可以保留研究，但不能因为更有弹性就绕过证据门槛。</p><h3>更符合当前风险预算的起步</h3><p>若要试验进攻风格，可先在<b>原20%首批股票预算内预留最多2%</b>，例如NVDA、AVGO、ANET、MRVL每只0.5%的条件性研究样例；其余首批最多18%。任何一只未通过资格、价格或事实验证，就留现金，不把额度转给其余股票。已有持仓及未成交买单也必须占用总预算。</p><p>确认后进攻总额最多8%，与之前科技/AI8%是同一个桶；其中超跌反弹子预算最多4%、高风险主题示例最多2%，均为包含关系。用户20%单股上限不是建议仓位。以上更紧阈值是本报告提出的管理纪律，并非用户新设硬规则。</p>')

stressrows=[]
for name,m in A['models'].items():
    stressrows.append([E(name),'；'.join(t+' '+str(v)+'%' for t,v in m['shock_assumptions_pct'].items()),pct(m['attack_scenario_impact_pct']),pct(m['combined_with_core_recession_pct']),pct(m['all_attack_down70_combined_pct'])])
body+=sec('risk','进攻仓的收益贡献与失败方式','<p>参考核心42%沿用旧衰退冲击时，损失约7.53%净值；新增进攻部分按下列主观下跌幅度计算。冲击没有概率，也不是最大损失。新股历史不完整，不能把此表称作新组合波动率或回撤预测。</p>'+table(['示例','个股主观压力','进攻部分净值影响','加上核心衰退','若全部进攻股跌70%'],stressrows)+'<p><b>关键限制：</b>8%进攻仓同时下跌70%，加上参考核心冲击约亏13.13%，已经超过12%容忍度。止损单、分散到更多股票和普通股形式都无法保证把跳空损失锁在12%。多个AI、存储、加密或航天股票可能在同一风险偏好冲击下同时下跌。</p><p>收益贡献也需要校准：若核心不动，8%进攻仓上涨25%或50%，分别只贡献约2%或4%净值收益；若想仅靠这8%使全组合上涨10%，其涨幅需约125%。这只是固定权重的算术，说明小进攻仓能提高参与度，却不能保证比赛排名跃升。</p><div class="calc"><h3>改变进攻假设，查看净值影响</h3><label>进攻总额（占净值%，0—8）<input id="size" type="number" min="0" max="8" step="0.25" value="8"></label><label>进攻股统一涨跌（%，-100—100）<input id="move" type="number" min="-100" max="100" step="5" value="-35"></label><button id="calculate">计算假设影响</button><div id="result" aria-live="polite"></div><p class="formnote">核心固定42%，继续使用-7.53%净值的主观衰退冲击；剩余为现金，现金收益0。不改变真实账户。</p></div>'+table(['风险闸门','处理'],[
 ['价格确认','至少开盘观察30分钟；确认最新完整交易日高低点、相对QQQ/SMH及可比时段成交量。高开超过3%先等，不把缺数据的VWAP/ATR写成已确认'],
 ['公司事件','已知财报前，新事件仓默认0；实际结果和电话会解释之后，重新核对经营、现金、指引、预期与价格反应'],
 ['论点失效','指引下调、回款转弱、融资代价上升、合同执行延迟、监管限制或里程碑延期，先重估；不能仅靠价格止损管理'],
 ['组合回撤','4%停止新增；6%复核并参考股票≤35%；8%参考≤20%；10%压低风险；12%视为预算失效。跳空时可能越级'],
 ['流动性','本轮只有周五成交额，不足以计算稳健退出天数；账户净值、实际深度与低成交日容量未知，不能保证所有规模都可退出']]))

events=[]
for t,s in S.items():
    ev=s['next_week_event'];date=ev.get('date_et')
    if date and '2026-10-26'<=date<='2026-10-30':
        found=re.search(r'(\d{1,2}:\d{2})',txt(ev.get('time_et')))
        cn='未核实'
        if found:
            dt=datetime.datetime.fromisoformat(date+'T'+found.group(1).zfill(5))+datetime.timedelta(hours=12);cn=dt.strftime('%m/%d %H:%M')
        events.append({'ticker':t,'date_et':date,'time_et':ev.get('time_et'),'beijing_reference':cn,'status':ev.get('status'),'note':ev.get('note'),'source_id':ev.get('source_id')})
events.sort(key=lambda e:(e['date_et'],e['ticker']))
(P/'attack_events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
body+=sec('events','下周事件与进攻节奏',table(['股票','日期ET','原文时点/窗口ET','北京时间参考','状态与说明','来源'],[[sl(e['ticker']),e['date_et'],E(txt(e['time_et'])),e['beijing_reference'],E(status(e['status']))+'；'+E(txt(e['note'])),ref(e['source_id'])] for e in events])+'<p>表内优先区分电话会与首次发布，不能将未核实的新闻稿分钟当作已确认。10/26—30北京比纽约快12小时；11/1后变成13小时。WDC与TSLA已发布最新财报，RKLB、TEM、ALAB等周后事件见个股页，不冒充下周催化。</p><p>周一/二优先观察已公布事实的盈利兑现型；周二STX/HOOD结果后再复核；周三GEV/VRT结果与FOMC叠加；周四SNDK/COIN/MSTR等事件前保留选择权；周五按已发布事实重排，不预写“超预期”。宏观日历及原五天报告仍是共同约束。</p>')
body+=sec('files','完整个股页面与可复核材料',table(['文件','内容'],[
 ['<a href="attack_candidates.csv">28股价格与分类CSV</a>','16新公司+12原候选；估值字段保留GAAP历史口径'],
 ['<a href="attack_model_weights.csv">三种配置示例CSV</a>','包含原参考核心、进攻权重与现金；不是订单'],
 ['<a href="attack_research.json">完整结构化研究</a> / <a href="attack_events.json">事件登记</a>','公司事实、原始来源、缺失和压力假设'],
 ['<a href="sources.html">来源登记</a> / <a href="validation.json">核验记录</a>','事实与日期的证据边界、计算及页面检查'],
 ['<a href="../weekly_expanded_20261026_30.html">55股与五天预选报告</a>','保留既有约束及历史时点'],
 ['<a href="../../2026-10-24/closing_update/monday_close_update_20261024.html">原组合与风控依据</a>','原20/35/50阶段，以及42%核心来源']])+f'<p>本页共{len(S)}家公司、{len(A["new_tickers"])}家新增，来源登记共{len(SRC)}条。新16股公司事实来自本轮已读披露，旧12股保留此前一手来源。本轮没有扩大已设置的五天盘前自动任务范围，也未执行交易。</p>')
script='''<script>function calc(){const a=Number(document.querySelector('#size').value),r=Number(document.querySelector('#move').value),o=document.querySelector('#result');if(!Number.isFinite(a)||!Number.isFinite(r)||a<0||a>8||r< -100||r>100){o.textContent='请输入0—8%的进攻总额及-100—100%的涨跌假设。';return;}const impact=a*r/100,total=-7.53+impact;o.innerHTML=`<p class="bigresult ${total<=-12?'bad':''}">进攻部分：${impact.toFixed(2)}%净值；含核心衰退：${total.toFixed(2)}%净值</p><p>参考现金 ${(58-a).toFixed(2)}%；${total<=-12?'已超过12%容忍预算，不能据此扩大仓位。':'此假设未触及12%，不代表真实损失受限。'}</p>`;}document.querySelector('#calculate').addEventListener('click',calc);calc();</script>'''
doc=page('进攻型股票：28个候选与三种风险预算',body)
(P/'aggressive_equity_20261025.html').write_text(doc.replace('</body>',script+'</body>'),encoding='utf-8')

(P/'stocks').mkdir(exist_ok=True)
for t,s in S.items():
    m=M[t]; pe=m.get('pe_ttm')
    attack=s.get('attack_case',s.get('rebound_case',''))
    expectation=s.get('expectations_risk','缺少完整正常化估值与同口径预期修正数据，不能声称已验证预期差。')
    b=f'<p class="lede">{E(m["attack_group"])} · {E(rank[t])}</p><div class="notice">{notice}</div>'+table(['收盘$','5日','10日','半年','GAAP TTM P/E','周五成交额$bn'],[[f(m['close']),pct(m['r5']),pct(m['r10']),pct(m['r_halfyear']),f(pe) if pe is not None and pe>0 else 'NM',f(m['turnover_friday_dollars']/1e9)]])
    if t in comment:b+='<p><b>本轮判断：</b>'+E(comment[t])+'</p>'
    b+=sec('facts','经营驱动与现金核验',f'<p><b>披露期间：</b>{E(txt(s["fiscal_period"]))}。<b>业务路径：</b>{E(txt(s["pathway"]))}</p><ul>'+''.join('<li>'+E(txt(x['claim']))+' '+ref(x['source_id'],'../')+'</li>' for x in s['facts'])+'</ul><p><b>公司指引：</b>'+prose(s['guidance'],'../')+'</p><p><b>现金质量：</b>'+prose(s['cash_quality'],'../')+'</p>')
    b+=sec('case','进攻论点、预期门槛与反方','<p><b>进攻论点（研究判断）：</b>'+prose(attack,'../')+'</p><p><b>市场期待与估值限制：</b>'+prose(expectation,'../')+'</p><p><b>最强反例：</b>'+prose(s['trap_case'],'../')+'</p><p><b>否决：</b>'+prose(s['kill'],'../')+'</p><p><b>从观察升级的证据：</b>'+prose(s['trigger'],'../')+'</p>')
    ev=s['next_week_event']
    b+=sec('events','事件与仓位边界','<p><b>已核验状态：</b>'+E(status(ev.get('status')))+'。日期 '+E(txt(ev.get('date_et')) or '下周未取得明确日期，周后安排见说明')+'；时间 '+E(txt(ev.get('time_et')) or '下周明确时点未核实')+'。'+E(txt(ev.get('note')) or '')+'</p>'+refs(s['source_ids'],'../')+'<p>供应商TTM是GAAP历史分母，不是正常化前瞻倍数。除明确已计算的公司现金桥外，不把一次性收益、预付款或融资流入视作持续经营利润；不同公司期间与口径不直接横比。</p>')
    inplans=[(name,w[t]) for name,w in ((n,m['attack']) for n,m in A['models'].items()) if t in w]
    b+='<p><b>示例关联：</b>'+('；'.join(E(name)+' '+f(w)+'%总净值（条件目标）' for name,w in inplans) if inplans else '未进入本轮配置示例，保留研究/观察')+'。这些是互斥研究情景，不可相加；起步试仓属于原20%首批预算，确认后进攻最多8%且包含已有科技风险，财报前新事件仓默认0。</p>'
    if t in A['retained_tickers']:b+=f'<p><a href="../../stocks/{safe(t)}.html">查看此前完整个股研究 →</a></p>'
    (P/'stocks'/f'{safe(t)}.html').write_text(page(t+' · '+m['name']+' 进攻研究',b,'../'),encoding='utf-8')
ledger=''
for s in A['sources']:
    ledger+=f'<article id="{E(s["id"])}" class="source"><h3>{E(s["id"])}</h3><p><a href="{E(s["url"])}">{E(s["title"])}</a></p><p class="meta">{E(txt(s.get("source_type")))} · 发布：{E(txt(s.get("published")))} · 查阅：{E(txt(s.get("accessed")))}</p></article>'
(P/'sources.html').write_text(page('进攻研究来源登记',ledger),encoding='utf-8')
(P/'priorities.json').write_text(json.dumps({'status':rank,'priority_notes':comment},ensure_ascii=False,indent=2),encoding='utf-8')
print('Built overview,28individual pages,source ledger and',len(events),'next-week event rows.')
