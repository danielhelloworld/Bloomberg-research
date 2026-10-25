from pathlib import Path
import json,csv,math,datetime
P=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def data(i):return json.loads(next(c['text'] for c in read(P/'data'/f'snapshot_{i}.json')['content'] if c['type']=='text'))
previous=read(P.parent/'expanded_research.json')
reuse=['NVDA','AMD','AVGO','MU','ANET','VRT','PLTR','CRWD','SNOW','CEG','VST','ORCL']
lanes=[read(P/'lanes'/name) for name in ['ai_hardware.json','platform_crypto.json','space_storage.json']]
new={s['ticker']:s for lane in lanes for s in lane['stocks']}
assert len(new)==16
q={s['symbol'].removesuffix('.US'):s for s in data(0)}
idx={s['symbol'].removesuffix('.US'):s for s in data(1)}
static={s['symbol'].removesuffix('.US'):s for s in data(2)}
assert set(q)==set(idx)==set(static)==set(new)
sources=[]
for lane in lanes:sources.extend(lane['sources'])
needed=set(id for t in reuse for id in previous['new_stocks'][t]['source_ids'])
sources.extend(s for s in previous['sources'] if s['id'] in needed)
assert len({s['id'] for s in sources})==len(sources)
facts={t:previous['new_stocks'][t] for t in reuse};facts.update(new)
facts['ASTS']=dict(facts['ASTS'])
facts['ASTS']['trigger']='当前只观察；最新现金桥、部署/服务收入与监管证据全部通过后，才讨论高风险未来条件示例最多0.25%总净值；任何缺口未关闭均不新建仓，并保留现金。'
metrics={t:previous['metrics'][t] for t in reuse}
for t,x in q.items():
    assert x['trade_status']=='Normal' and x['timestamp'].startswith('2026-10-23T20:00:0')
    a=idx[t];close=float(x['last_done']);prev=float(x['prev_close'])
    assert abs(close-float(a['last_done']))<=.011
    assert float(x['low'])<=close<=float(x['high']) and close>0
    metrics[t]={'name':static[t]['name_cn'] or static[t]['name_en'],'close':close,'r1':(close/prev-1)*100,'r5':float(a['five_day_change_rate']),'r10':float(a['ten_day_change_rate']),'r_halfyear':float(a['half_year_change_rate']),'pe_ttm':float(a['pe_ttm_ratio']),'high':float(x['high']),'low':float(x['low']),'turnover_friday_dollars':float(x['turnover']),'volume_friday':float(x['volume']),'quote_timestamp':x['timestamp'],'rsi14':None,'atr14':None,'beta':None}
groups={
 '盈利与现金兑现':['NVDA','AVGO','ANET','MRVL','GEV','STX','WDC','SNDK','CEG','VST','CRWD'],
 '增长加速与高预期':['AMD','MU','ALAB','PLTR','VRT','SNOW'],
 '资本开支与融资约束':['CRWV','NBIS','ORCL'],
 '高弹性主题与市场交易':['TSLA','HOOD','COIN','MSTR','RKLB','ASTS'],
 '医疗商业化与监管':['TEM','HIMS']}
assert set(t for names in groups.values() for t in names)==set(facts)==set(metrics)
assert sum(map(len,groups.values()))==28
for g,names in groups.items():
    for t in names:metrics[t]['attack_group']=g
plans={
 '盈利兑现型':{'NVDA':2,'AVGO':1.5,'ANET':1.5,'MRVL':1,'GEV':1,'STX':1},
 '高增长验证型':{'NVDA':2,'ALAB':1.5,'PLTR':1.5,'VRT':1.5,'MRVL':1.5},
 '高风险主题观察型':{'HOOD':.75,'COIN':.5,'TSLA':.5,'ASTS':.25}}
shocks={
 '盈利兑现型':{'NVDA':-30,'AVGO':-30,'ANET':-35,'MRVL':-35,'GEV':-25,'STX':-35},
 '高增长验证型':{'NVDA':-35,'ALAB':-50,'PLTR':-50,'VRT':-40,'MRVL':-40},
 '高风险主题观察型':{'HOOD':-60,'COIN':-65,'TSLA':-50,'ASTS':-75}}
oldrisk=read(P.parent.parent/'2026-10-24/closing_update/analysis_close.json')
core={t:v for t,v in oldrisk['models']['修订B_50'].items() if t not in ['CASH','MSFT','GOOGL'] and v>0}
assert sum(core.values())==42
core_loss=sum(w*oldrisk['stress_vectors']['需求衰退，能源保护失效'].get(t,0)/100 for t,w in core.items())
model={}
for name,w in plans.items():
    attack=sum(w.values());cash=58-attack; loss=sum(w[t]*shocks[name][t]/100 for t in w)
    assert attack<=8 and max(w.values())<=2 and 42+attack+cash==100
    model[name]={'attack':w,'attack_pct':attack,'reference_core':core,'reference_core_pct':42,'cash_pct':cash,'total_equity_pct':42+attack,'shock_assumptions_pct':shocks[name],'attack_scenario_impact_pct':loss,'combined_with_core_recession_pct':core_loss+loss,'all_attack_down70_combined_pct':core_loss-attack*.7,
       'attack_rises25_core_flat_NAV_pct':attack*.25,'attack_rises50_core_flat_NAV_pct':attack*.5}
out={'as_of_beijing':'2026-10-25; regular-session prices10/23','coverage':{'this_report':28,'new_companies':16,'retained_prior_companies':12,'combined_unique_companies_across_reports':71},'metrics':metrics,'stocks':facts,'sources':sources,'groups':groups,'new_tickers':list(new),'retained_tickers':reuse,'models':model,'core_recession_impact_pct':core_loss,
 'constraints':{**previous['constraints'],'attack_sleeve_max_pct':8,'attack_sleeve_is_same_budget_as_prior_tech_AI':True,'first_pilot_total_pct':2,'high_risk_theme_example_max_pct':2,'max_single_pct_user':20,'plan_status':'mutually exclusive hypothetical research allocations, no actual holdings or orders'},
 'data_limits':{'new_history':'unavailable; no RSI/ATR/historical beta/covariance/backtest claims','valuation':'provider GAAP TTM only; not normalized forward multiples; no price targets','WLS':'not verified; ordinary stock/ADR form and current eligibility must be checked','quotes':'regular-session last_done, not Monday executable prices','expected_return':'not estimated; upside contributions are simple hypothetical arithmetic','automation':'existing five-day55-stock update not changed by this independent report'},
 'method':'Qualitative attack archetypes and issuer evidence, not optimized return rankings. Scenario shocks illustrative; original42%core recession vector retained for comparison, not a validated new portfolio risk forecast.'}
(P/'attack_research.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
with (P/'attack_candidates.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['ticker','name','attack_group','close','r1','r5','r10','r_halfyear','pe_ttm','turnover_friday_dollars','quote_timestamp'];writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader()
    for t,m in metrics.items():writer.writerow({'ticker':t,**m})
with (P/'attack_model_weights.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['model','ticker','hypothetical_total_NAV_weight_pct','assumed_stock_shock_pct','status'])
    for name,m in model.items():
        for t,w in m['reference_core'].items():writer.writerow([name,t,w,'','retained_reference_core'])
        for t,w in m['attack'].items():writer.writerow([name,t,w,m['shock_assumptions_pct'][t],'conditional_example_only'])
        writer.writerow([name,'CASH',m['cash_pct'],'','conditional_example_only'])
print(json.dumps({'coverage':out['coverage'],'sources':len(sources),'core_loss':core_loss,'models':{n:{k:m[k] for k in ['attack_pct','cash_pct','attack_scenario_impact_pct','combined_with_core_recession_pct','all_attack_down70_combined_pct']} for n,m in model.items()}},ensure_ascii=True))
