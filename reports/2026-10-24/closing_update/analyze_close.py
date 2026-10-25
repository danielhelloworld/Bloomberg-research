"""Reproducible refresh; preserves all original provider/history files."""
from pathlib import Path
import json, csv, math
import numpy as np
import pandas as pd

P=Path(__file__).resolve().parent
BASE=P.parent
OLD=BASE.parent/'2026-10-23'
prior=json.loads((BASE/'risk_comparison.json').read_text(encoding='utf-8'))
snap=json.loads((P/'closing_quotes.json').read_text(encoding='utf-8'))
quotes={q['symbol'].removesuffix('.US'):q for q in snap['quotes']}
history={}
for filename in ['stock_raw.json','market_raw.json']:
    history.update(json.loads((OLD/filename).read_text(encoding='utf-8'))['history'])
assert len(quotes)==48 and set(quotes)==set(history)
series={}; metrics={}; discrepancies=[]
for s,rows in history.items():
    f=pd.DataFrame(rows,columns=['date','price','volume'])
    f['date']=f.date.str[:10]
    f=f[f.date<'2026-10-23'].set_index('date').astype(float).sort_index()
    assert len(f)==259 and f.index.is_unique and f.index[-1]=='2026-10-22'
    q=quotes[s]; last=float(q['last_done']); prev=float(q['prev_close'])
    assert q['trade_status']=='Normal' and q['timestamp'].startswith('2026-10-23T20:00:0')
    if abs(float(f.price.iloc[-1])-prev)>0.0001:
        discrepancies.append({'ticker':s,'old_history_prev':float(f.price.iloc[-1]),'latest_quote_prev':prev,'difference_dollars':prev-float(f.price.iloc[-1]),'difference_bps':(prev/float(f.price.iloc[-1])-1)*1e4,'handling':'keep original history; quote day change and appended-series day change labeled separately'})
    f.loc['2026-10-23']=[last,float(q['volume'])]
    a=f.price; r=np.log(a/a.shift()).dropna()
    assert len(r)==259 and (a>0).all() and (f.volume>=0).all()
    series[s]=a
    metrics[s]={'close':last,'quote_prev_close':prev,'quote_r1':(last/prev-1)*100,'series_r1':(last/a.iloc[-2]-1)*100,
                **{f'r{k}':(last/a.iloc[-k-1]-1)*100 for k in [5,10,21,63]},
                **{f'ma{k}':float(a.tail(k).mean()) for k in [20,50,200]},
                'vol20':float(r.tail(20).std()*math.sqrt(252)*100),'vol60':float(r.tail(60).std()*math.sqrt(252)*100),
                'drawdown_from_sample_high':float((last/a.max()-1)*100),'sample_max_drawdown':float((a/a.cummax()-1).min()*100),
                'adv20_shares':float(f.volume.tail(20).mean()),'dollar_volume_proxy20':float((f.price*f.volume).tail(20).mean())}
prices=pd.DataFrame(series).sort_index()
assert prices.shape==(260,48) and not prices.isna().any().any()
rets=np.log(prices/prices.shift()).dropna()
models=dict(prior['models'])
models['修订B条件35']={s:(v*.7 if s!='CASH' else 65) for s,v in models['修订B_50'].items()}
risk={}
for name,w in models.items():
    assert math.isclose(sum(w.values()),100) and min(w.values())>=0
    sy=[s for s,v in w.items() if s!='CASH' and v>0]
    vec=np.array([w[s]/100 for s in sy]); windows={}
    for n in [20,60,120,252]:
        rr=rets[sy].tail(n); cov=rr.cov().to_numpy(); sig=rr.std().to_numpy(); corr=rr.corr().to_numpy()
        shifted=np.diag(sig)@(.5*corr+.5*np.ones_like(corr))@np.diag(sig)
        windows[str(n)]={'vol':float(math.sqrt(vec@cov@vec)*math.sqrt(252)*100),'correlation_shift_vol':float(math.sqrt(vec@shifted@vec)*math.sqrt(252)*100),'all_positive_one_vol':float(sum(vec*sig)*math.sqrt(252)*100),'start':rr.index[0],'end':rr.index[-1]}
    rr=rets[sy].tail(60); cov=rr.cov().to_numpy(); pr=rr.to_numpy()@vec
    beta={b:float(np.cov(pr,rets.loc[rr.index,b],ddof=1)[0,1]/rets.loc[rr.index,b].var()) for b in ['SPY','ACWI']}
    contributions=vec*(cov@vec)/(vec@cov@vec)*100
    risk[name]={'equity':100-w['CASH'],'cash':w['CASH'],'gross_equity_pct':100-w['CASH'],'net_equity_pct':100-w['CASH'],'windows':windows,'beta_proxy':beta,'beta_adjusted_SPY_exposure_pct':beta['SPY']*100,
        'scenario':{label:sum(w.get(s,0)*shock/100 for s,shock in shocks.items()) for label,shocks in prior['stress_vectors'].items()},
        'variance_contributions':dict(zip(sy,map(float,contributions))),
        'hypothetical_friday_at_fixed_weights':sum(w.get(s,0)*metrics[s]['series_r1']/100 for s in sy),
        'single_name_scenario_losses':{s:-w.get(s,0)*prior['individual_shock_assumptions'][s] for s in prior['individual_shock_assumptions']},
        'exit_days_at_5pct_ADV_per_1m_NAV':{s:(1e6*w[s]/100)/(metrics[s]['dollar_volume_proxy20']*.05) for s in sy}}
# Quantify the sole previous-close discrepancy without revising the source series.
alt=prices.copy(); alt.loc['2026-10-22','PG']=float(quotes['PG']['prev_close'])
altret=np.log(alt/alt.shift()).dropna()
w=models['修订B_50']; sy=[s for s,v in w.items() if s!='CASH' and v>0]; v=np.array([w[s]/100 for s in sy])
altvol=float(np.std(altret[sy].tail(60).to_numpy()@v,ddof=1)*math.sqrt(252)*100)
source_notes=[{'id':'Q1','name':'Longbridge regular-session quote snapshot','file':'closing_quotes.json','captured_utc':snap['captured_utc'],'as_of':'2026-10-23 16:00 ET regular session; post_market excluded','limits':'History by-date endpoint denied permission 301607. Latest quote is not independently historical-bar verified. Historical adjusted series retained; latest quote appended, no corporate-action reconciliation beyond previous-close comparison.'},
 {'id':'H1','name':'Original 259 provider adjusted daily closes','file':'../../2026-10-23/stock_raw.json','as_of':'through 2026-10-22','limits':'price-return approximation, excludes cash yield, transaction costs, execution slippage and full total-return adjustment verification'},
 {'id':'M1','name':'Bloomberg market wrap syndicated by SWI','url':'https://www.swissinfo.ch/eng/stocks-fall-as-oil-rally-keeps-a-lid-on-treasuries:-markets-wrap/92260391','as_of':'2026-10-23 New York 16:00 snapshot; page updated Oct23 22:05','facts':{'US_10y_yield_pct':5.00,'change_bps':5,'WTI_snapshot_usd':103.63,'WTI_change_pct':4.2,'spot_gold_snapshot_usd':3999.56},'limits':'news snapshot, not independently verified exchange settlement or bond-close feed'},
 {'id':'E1','name':'Federal Reserve October calendar','url':'https://www.federalreserve.gov/newsevents/2026-october.htm','facts':'October27–28 FOMC; Oct28 14:00 ET decision,14:30 press conference'},
 {'id':'E2','name':'BEA official release schedule','url':'https://www.bea.gov/news/schedule/full','facts':'Oct29 08:30 ET Q3 advance GDP and September personal income/outlays'}]
out={'session_date':'2026-10-23','captured_utc':snap['captured_utc'],'price_rows':len(prices),'return_rows':len(rets),'metrics':metrics,'models':models,'risk':risk,'stress_vectors':prior['stress_vectors'],'individual_shock_assumptions':prior['individual_shock_assumptions'],
 'user_constraints':{**prior['user_constraints'],'cash_rules':'User explicitly confirms 50% and 80% cash allowed on 2026-10-24; not independent handbook verification'},
 'previous_close_discrepancies':discrepancies,'PG_alternative_prev_close_60d_vol':altvol,'PG_vol_sensitivity_pp':altvol-risk['修订B_50']['windows']['60']['vol'],
 'sector_proxy_up_count':sum(metrics[s]['quote_r1']>0 for s in ['XLK','XLF','XLV','XLE','XLI','XLP','XLY','XLU','XLB','XLRE','XLC']),
 'sector_proxy_total':11,'corr60':rets.tail(60).corr().to_dict(),'source_notes':source_notes,
 'method':'Sample covariance of weighted daily log returns, annualized sqrt252, cash zero. Fixed weights, no expected-return optimization, no strategy performance evidence. ETF country returns are US-traded USD wrappers and include FX, session mismatch and market structure. Quotes are not executable Monday orders.'}
(P/'analysis_close.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'source_notes.json').write_text(json.dumps(source_notes,ensure_ascii=False,indent=2),encoding='utf-8')
prices.to_csv(P/'aligned_prices.csv',encoding='utf-8-sig',index_label='date')
pd.DataFrame(metrics).T.to_csv(P/'close_metrics.csv',encoding='utf-8-sig',index_label='ticker')
pd.DataFrame(models).to_csv(P/'allocations_close.csv',encoding='utf-8-sig',index_label='ticker')
print(json.dumps({'counts':[len(quotes),len(prices),len(rets)],'discrepancies':discrepancies,'pg_vol_sensitivity_pp':out['PG_vol_sensitivity_pp'],'risk':{n:{'vol60':r['windows']['60']['vol'],'vol20':r['windows']['20']['vol'],'corrshift60':r['windows']['60']['correlation_shift_vol'],'beta':r['beta_proxy'],'friday_illustration':r['hypothetical_friday_at_fixed_weights']} for n,r in risk.items()}},ensure_ascii=False))
