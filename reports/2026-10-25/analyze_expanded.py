from pathlib import Path
from collections import Counter
import json,csv,math,datetime
P=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def provider(n):
    r=read(P/'data'/f'fetch_{n}.json')
    return json.loads(next(c['text'] for c in r['content'] if c['type']=='text'))
quotes={r['symbol'].removesuffix('.US'):r for r in provider(1)}
indexes={r['symbol'].removesuffix('.US'):r for r in provider(2)}
static={r['symbol'].removesuffix('.US'):r for r in provider(3)}
old=read(P.parent/'2026-10-24/closing_update/analysis_close.json')
oldstocks=read(P.parent/'2026-10-24/stock_research_synthesis.json')['stocks']
lanes=[read(P/'lanes'/f) for f in ['semiconductors.json','software_platforms.json','infrastructure_cyclicals.json']]
newstocks={s['ticker']:s for lane in lanes for s in lane['stocks']}
assert len(quotes)==55 and len(indexes)==len(newstocks)==len(static)==40
assert set(quotes)==set(oldstocks)|set(newstocks)
sources=read(P/'root_sources.json')
for lane in lanes:sources.extend(lane['sources'])
oldsrc=read(P.parent/'2026-10-24/source_register.json')
for s in oldsrc:sources.append({'id':'OLD-'+str(s['id']),'url':s['url'],'title':s['ticker']+' prior primary disclosure','published':s['date'],'accessed':'2026-10-24 prior report','source_type':'retained prior research'})
ids=[s['id'] for s in sources]
assert len(ids)==len(set(ids)),'Source IDs must be unique across lanes'
metrics={};conflicts=[]
for t,q in quotes.items():
    assert q['timestamp'].startswith('2026-10-23T20:00:0') and q['trade_status']=='Normal'
    close=float(q['last_done']);prev=float(q['prev_close']);volume=float(q['volume']);turn=float(q['turnover'])
    assert close>0 and prev>0 and volume>0 and turn>0
    m={'close':close,'prev_close':prev,'r1':(close/prev-1)*100,'open':float(q['open']),'high':float(q['high']),'low':float(q['low']),'volume_friday':volume,'turnover_friday_dollars':turn,'quote_timestamp':q['timestamp'],'wls':'unverified','rsi14':None,'atr14':None,'drawdown52w':None}
    assert m['low']<=close<=m['high']
    if t in indexes:
        x=indexes[t]
        for a,b in [('r5','five_day_change_rate'),('r10','ten_day_change_rate'),('r_halfyear','half_year_change_rate'),('pe_ttm','pe_ttm_ratio'),('pb','pb_ratio'),('market_cap','total_market_value'),('volume_ratio','volume_ratio')]:
            m[a]=float(x[b]) if x.get(b) not in ['',None] else None
        delta=float(x['last_done'])-close
        if abs(delta)>.011:conflicts.append({'ticker':t,'quote_close':close,'calc_last_done':x['last_done'],'difference':delta})
        m['return_source']='Longbridge calc snapshot; period endpoints not independently supplied; last_done matched to quote'
        m['name']=static[t]['name_cn'] or static[t]['name_en']
    else:
        x=old['metrics'][t]
        m.update({'r5':x['r5'],'r10':x['r10'],'r_halfyear':None,'pe_ttm':None,'pb':None,'market_cap':None,'volume_ratio':None,'name':oldstocks[t]['name'],'return_source':'retained aligned adjusted history through10/23; may differ slightly from live calc definition'})
    if m['r10']<=-10 and m['r5']<=0:m['price_bucket']='短期急跌待确认'
    elif m['r10']<0 and m['r5']>0:m['price_bucket']='已反弹等待回踩'
    elif m['r10']>=0:m['price_bucket']='非超跌/强势对照'
    else:m['price_bucket']='温和回撤观察'
    m['high_runup_warning']=bool(m['r_halfyear'] is not None and m['r_halfyear']>50 and m['r10']<=-10)
    m['pe_use']='NM: negative GAAP earnings' if m['pe_ttm'] is not None and m['pe_ttm']<=0 else 'GAAP TTM snapshot only; denominator and adjusted/future earnings not reconciled'
    metrics[t]=m
assert not conflicts,conflicts
# A research ordering, never a return-maximization score or executable ranking.
research_priority=['NVDA','TSM','AVGO','META','ANET','NFLX','LRCX','VRT','MU','ASML','AMAT','KLAC','AMD','ORCL','ARM','INTC','CEG','VST','PANW','CRWD','DDOG','SNOW','QCOM','UBER','PLTR','AAPL','CRM','ADBE','NOW','ZS','V','MA','CAT','RTX','GE','LLY','UNH','COST','BAC','SLB']
days=[
 {'date':'2026-10-26','label':'周一','theme':'已披露业绩的质量修复；保留事件前现金','names':['NVDA','TSM','AVGO','META','NFLX','LRCX','AMAT','ANET','VRT','ORCL','PG','JPM'],'focus':['NVDA','TSM','META','NFLX'],'wait':['VRT','AMAT','ORCL'],'rule':'只用已公开事实与周一实时价格判断。新反弹仓位合计最多2%总净值，必须在既有首批20%股票预算内替换，不额外叠加。尚未核验WLS或没有价格确认则0。'},
 {'date':'2026-10-27','label':'周二','theme':'消费信心与支付链；财报前筛查','names':['V','MA','CAT','LLY','UNH','BAC','COST','UBER','ADBE','CRM','MSFT','GOOGL'],'focus':['UNH','BAC','UBER','ADBE'],'wait':['V','MA','CAT','LLY','MSFT','GOOGL'],'rule':'先更新周一收盘，再筛选。支付、消费与工业股验证需求，不把非超跌股硬归为反弹；V盘后财报前默认不新开隔夜事件仓。'},
 {'date':'2026-10-28','label':'周三','theme':'FOMC叠加科技财报；以等待和比较为主','names':['V','VRT','NOW','KLAC','MSFT','GOOGL','NVDA','TSM','ANET','PANW','CRWD','DDOG'],'focus':['V','NVDA','TSM','ANET'],'wait':['VRT','NOW','KLAC','MSFT','GOOGL'],'rule':'V需先读周二实际结果；VRT盘前结果与11:00ET电话会后再核查。FOMC14:00ET公布前暂停扩张反弹风险；盘后科技财报未发布前不能写出结果。'},
 {'date':'2026-10-29','label':'周四','theme':'宏观与云软件结果验证；拒绝只看EPS跳升','names':['MSFT','GOOGL','NOW','KLAC','VRT','MA','CAT','LLY','AMZN','INTC','NVDA','ORCL'],'focus':['MSFT','GOOGL','NOW','KLAC','VRT'],'wait':['AMZN','INTC'],'rule':'盘前GDP/PCE与前一晚财报都必须实际取得；分开收入、现金、资本开支、指引与股价反应。MA/CAT/LLY当日结果先读后评，AMZN/INTC盘后前默认0新事件仓。'},
 {'date':'2026-10-30','label':'周五','theme':'亚马逊与英特尔复盘；油企/医疗财报；周末风险','names':['AMZN','INTC','XOM','CVX','ABBV','MA','CAT','LLY','META','ANET','AAPL','PLTR'],'focus':['AMZN','INTC','META','ANET'],'wait':['XOM','CVX','ABBV','AAPL','PLTR'],'rule':'油企与ABBV数据公布后再评现金质量，不能在公告前预设通过。周末前不为赶进度补满；AAPL/PLTR下一周事件属于持仓跨周风险，而非本周已确认催化。'}]
for d in days:assert len(d['names'])==len(set(d['names']))==12 and set(d['names'])<=set(quotes)
base=old['models']['修订B_50']
core={t:v for t,v in base.items() if t not in ['CASH','MSFT','GOOGL']}
assert sum(core.values())==42
core_recession=sum(v*old['stress_vectors']['需求衰退，能源保护失效'].get(t,0)/100 for t,v in core.items())
stress=[]
for tech in [2,4,8]:
    for shock in [-20,-35,-50]:stress.append({'core_equity_pct':42,'replacement_tech_pct':tech,'cash_pct':58-tech,'core_assumed_recession_loss_pct':core_recession,'tech_shock_pct':shock,'tech_NAV_impact_pct':tech*shock/100,'combined_NAV_impact_pct':core_recession+tech*shock/100})
out={'as_of_beijing':'2026-10-25; last regular-session prices10/23','scope':{'total':55,'legacy':15,'additional':40,'daily_previews':5,'per_day_names':12,'ticker_day_rows':60,'unique_daily_names':len(set(t for d in days for t in d['names']))},'metrics':metrics,'new_stocks':newstocks,'legacy_stocks':oldstocks,'sources':sources,'days':days,'research_priority':research_priority,'funnel':dict(Counter(metrics[t]['price_bucket'] for t in newstocks)),'replacement_stress':stress,'core_recession_impact_pct':core_recession,
 'constraints':{**old['user_constraints'],'new_rebound_pilot_total_max_pct':2,'confirmed_rebound_subbucket_max_pct':4,'all_tech_AI_related_total_max_pct':8,'conditional_total_equity_max_pct':50,'pre_earnings_new_event_position_default_pct':0},
 'data_quality':{'quote_rows':55,'calc_rows':40,'static_rows':40,'calc_quote_conflicts':conflicts,'new_history':'unavailable; no RSI/ATR/52w-drawdown/covariance/backtest claims','daily_report_posture':'as-of Sunday conditional previews; future actual results and prices not fabricated','longbridge_history':'previously permission denied; not retried','financial_datasets':'balance zero; no credits purchased','public_history_probe':'Yahoo403 for2symbols; stopped'},
 'method':'Price buckets based on provider5/10day percentages; thresholds illustrative and not optimized. Research order is qualitative PM judgment; no expected-return, hit-rate or causal attribution claim. All candidate eligibility conditional on current WLS.'}
(P/'expanded_research.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
with (P/'candidate_metrics.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['ticker',*next(iter(metrics.values())).keys()]);writer.writeheader()
    for t,m in metrics.items():writer.writerow({'ticker':t,**m})
with (P/'daily_preselection.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['date_ET','ticker','role','as_of','requires_actual_refresh'])
    for d in days:
        for t in d['names']:writer.writerow([d['date'],t,'先研究' if t in d['focus'] else '事件等待' if t in d['wait'] else '条件观察','2026-10-25','true'])
print(json.dumps({'scope':out['scope'],'funnel':out['funnel'],'sources':len(sources),'price_conflicts':conflicts,'core_recession':core_recession},ensure_ascii=True))
