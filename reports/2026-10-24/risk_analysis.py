from pathlib import Path
import json,csv,math
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
OLD=P.parent/'2026-10-23'
D=json.loads((OLD/'analysis.json').read_text(encoding='utf-8'))
stocks=list(D['stock_plans']['B']); stocks.remove('CASH')
raw=json.loads((OLD/'stock_raw.json').read_text(encoding='utf-8'))['history']
mr=json.loads((OLD/'market_raw.json').read_text(encoding='utf-8'))['history']
prices=pd.DataFrame({s:pd.Series({t[:10]:float(p) for t,p,v in rows if t[:10]<'2026-10-23'}) for s,rows in {**raw,'ACWI':mr['ACWI']}.items()})
rets=np.log(prices/prices.shift(1)).dropna()
old=D['stock_plans']['B']
revised={'XOM':5,'CVX':3,'JNJ':5,'ABBV':3,'PG':7,'WMT':3,'JPM':6,'BRK.B':6,'MSFT':5,'GOOGL':3,'AMZN':0,'LMT':4,'ETN':0,'TM':0,'NEE':0,'CASH':50}
starter={'XOM':2,'CVX':1,'JNJ':3,'ABBV':0,'PG':3,'WMT':2,'JPM':4,'BRK.B':3,'MSFT':0,'GOOGL':0,'AMZN':0,'LMT':2,'ETN':0,'TM':0,'NEE':0,'CASH':80}
assert sum(revised.values())==100 and sum(starter.values())==100
assert all(starter[s]<=revised[s] for s in stocks)
assert max(revised[s] for s in stocks)<=20
scaled={s:old.get(s,0)*50/75 for s in stocks}; scaled['CASH']=50
models={'原B_75':old,'原B同比缩到50':scaled,'修订B_50':revised,'修订B周一20':starter}
scenarios=D['stress_vectors_pct'].copy()
event_shocks={'XOM':-12,'CVX':-12,'ABBV':-20,'MSFT':-15,'GOOGL':-18,'AMZN':-22,'ETN':-20}
scenarios['主要财报一起不及预期']=event_shocks
idiosyncratic={'XOM':-.18,'CVX':-.18,'JNJ':-.12,'ABBV':-.20,'PG':-.10,'WMT':-.20,'JPM':-.22,'BRK.B':-.18,'MSFT':-.20,'GOOGL':-.22,'AMZN':-.30,'LMT':-.20,'ETN':-.25,'TM':-.25,'NEE':-.25}
scenarios['个股风险同时出现']={s:v*100 for s,v in idiosyncratic.items()}
risk={}
for n,w in models.items():
 sy=[s for s in stocks if w.get(s,0)>0]; vec=np.array([w[s]/100 for s in sy]); vals={}
 for window in [20,60,120,252]:
  rr=rets[sy].tail(window); cov=rr.cov().values
  vol=math.sqrt(float(vec@cov@vec))*math.sqrt(252)*100
  corr=rr.corr().values; sigma=rr.std().to_numpy()
  # Raise diversification assumptions toward a common risk regime while preserving PSD.
  stressed_corr=.5*corr+.5*np.ones_like(corr)
  cov_stressed=np.diag(sigma)@stressed_corr@np.diag(sigma)
  shrinkvol=math.sqrt(float(vec@cov_stressed@vec))*math.sqrt(252)*100
  vals[str(window)]={'vol':vol,'correlation_shift_vol':shrinkvol,'all_positive_one_vol':float(sum(vec*sigma)*math.sqrt(252)*100),'start':rr.index[0],'end':rr.index[-1]}
 rr=rets[sy].tail(60); cov=rr.cov().values
 contrib=vec*(cov@vec)/(vec@cov@vec)*100
 paircorr=rr.corr().to_dict()
 capital_event=sum(w.get(s,0) for s in event_shocks)
 risk[n]={'equity':100-w['CASH'],'cash':w['CASH'],'windows':vals,'scenario':{label:sum(w.get(s,0)*v/100 for s,v in shocks.items()) for label,shocks in scenarios.items()},'variance_contributions':dict(zip(sy,[float(x) for x in contrib])),'event_exposure_potential':capital_event,'single_name_shocks':{s:-w.get(s,0)*idiosyncratic[s] for s in stocks},'worst_single_assumed_loss':max(-w.get(s,0)*idiosyncratic[s] for s in stocks)}
old_loss=-risk['原B_75']['scenario']['需求衰退，能源保护失效']; scaled_loss=-risk['原B同比缩到50']['scenario']['需求衰退，能源保护失效']; new_loss=-risk['修订B_50']['scenario']['需求衰退，能源保护失效']
decomp={'old_loss_pct':old_loss,'old_at_50_loss_pct':scaled_loss,'new_at_50_loss_pct':new_loss,'improvement_from_reducing_gross':old_loss-scaled_loss,'improvement_from_composition_at_equal_equity':scaled_loss-new_loss}
event_groups={'油企财报':['XOM','CVX'],'AI/云/电力设备':['MSFT','GOOGL','AMZN','ETN'],'医疗':['JNJ','ABBV'],'必需消费':['PG','WMT'],'金融/综合':['JPM','BRK.B']}
groups={label:{n:sum(w.get(s,0) for s in sy) for n,w in models.items()} for label,sy in event_groups.items()}
out={'cutoff':'2026-10-22 complete close; no Friday close yet','user_constraints':{'account':'Bloomberg Trading Challenge','current_holdings':'defensive assets; user authorizes planning as if 100% buying power can be reallocated; actual holdings not supplied','long_only':True,'common_stock_only':True,'max_single_pct':20,'max_drawdown_tolerance_pct':12,'cash_rules':'not verified','wls_eligibility':'not verified','initial_entry_completed':'user confirmed'},'models':models,'risk':risk,'stress_vectors':scenarios,'individual_shock_assumptions':idiosyncratic,'groups':groups,'improvement_decomposition':decomp,'corr60':rets[stocks].tail(60).corr().to_dict(),'liquidity_proxy':{s:D['metrics'][s]['dollar_volume_proxy'] for s in stocks},'method':'weighted log-return covariance approximation; no expected-return estimates, no return optimization or out-of-sample strategy claim; correlation stress =0.5*sample correlation+0.5*ones matrix; cash return zero'}
(P/'risk_comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
with (P/'revised_stock_allocations.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.writer(f);writer.writerow(['ticker','old_B_target_pct','revised_conditional_target_pct','Monday_conditional_pct','single_stock_max_pct_user','assumed_name_stress_pct','NAV_loss_at_revised_pct','WLS'])
 for s in [*stocks,'CASH']:writer.writerow([s,old.get(s,0),revised.get(s,0),starter.get(s,0),20 if s!='CASH' else '',idiosyncratic.get(s,0)*100,-revised.get(s,0)*idiosyncratic.get(s,0),'unverified'])
print(json.dumps({'decomposition':decomp,'groups':groups,'models':{n:{'equity':r['equity'],'vol60':r['windows']['60']['vol'],'vol120':r['windows']['120']['vol'],'vol252':r['windows']['252']['vol'],'corrshift60':r['windows']['60']['correlation_shift_vol'],'co_dir':r['windows']['60']['all_positive_one_vol'],'single_loss':r['worst_single_assumed_loss'],'stress':r['scenario']} for n,r in risk.items()}},ensure_ascii=False))
