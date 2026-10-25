from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, math, hashlib
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
A=json.loads((P/'analysis_close.json').read_text(encoding='utf-8'))
(P/'validation_close.json').write_text('{"passed":false,"status":"running"}',encoding='utf-8')
px=pd.read_csv(P/'aligned_prices.csv',index_col='date')
assert px.shape==(260,48) and px.index[-1]=='2026-10-23' and not px.isna().any().any()
assert px.index.is_unique and (px>0).all().all()
raw=json.loads((P/'closing_quotes.json').read_text(encoding='utf-8'))['quotes']
assert len(raw)==48 and len({q['symbol'] for q in raw})==48
for q in raw:
    t=q['symbol'].removesuffix('.US')
    assert math.isclose(px.loc['2026-10-23',t],float(q['last_done']),abs_tol=1e-10)
    assert math.isclose(A['metrics'][t]['quote_r1'],(float(q['last_done'])/float(q['prev_close'])-1)*100,abs_tol=1e-10)
assert [d['ticker'] for d in A['previous_close_discrepancies']]==['PG']
ret=np.log(px/px.shift()).dropna()
assert len(ret)==259
independent={}
recession={'XOM':-25,'CVX':-25,'JNJ':-12,'ABBV':-15,'PG':-10,'WMT':-14,'JPM':-28,'BRK.B':-18,'MSFT':-22,'GOOGL':-23,'AMZN':-25,'LMT':-15,'ETN':-28,'TM':-25,'NEE':-18}
for name,w in A['models'].items():
    assert math.isclose(sum(w.values()),100,abs_tol=1e-9)
    assert min(w.values())>=0 and max(v for s,v in w.items() if s!='CASH')<=20
    # Direct weighted return sample standard deviation, independent of covariance formula.
    series=sum(ret[s]*v/100 for s,v in w.items() if s!='CASH')
    independent[name]={}
    for n in [20,60,120,252]:
        vol=float(series.tail(n).std(ddof=1)*math.sqrt(252)*100)
        assert math.isclose(vol,A['risk'][name]['windows'][str(n)]['vol'],abs_tol=1e-10)
        independent[name][str(n)]=vol
    for label,shocks in A['stress_vectors'].items():
        impact=sum(w[s]/100*shocks.get(s,0) for s in w if s!='CASH')
        assert math.isclose(impact,A['risk'][name]['scenario'][label],abs_tol=1e-10)
    direct_recession=sum(w.get(s,0)*shock/100 for s,shock in recession.items())
    assert math.isclose(direct_recession,A['risk'][name]['scenario']['需求衰退，能源保护失效'],abs_tol=1e-10)
    assert math.isclose(sum(A['risk'][name]['variance_contributions'].values()),100,abs_tol=1e-8)
    for b in ['SPY','ACWI']:
        X=ret[b].tail(60).to_numpy(); Y=series.tail(60).to_numpy()
        beta=float(np.dot(X-X.mean(),Y-Y.mean())/np.dot(X-X.mean(),X-X.mean()))
        assert math.isclose(beta,A['risk'][name]['beta_proxy'][b],abs_tol=1e-10)
assert math.isclose(A['risk']['修订B_50']['scenario']['需求衰退，能源保护失效'],-9.32,abs_tol=1e-10)
assert 'User explicitly confirms' in A['user_constraints']['cash_rules']
assert A['user_constraints']['max_drawdown_tolerance_pct']==12
class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
root=P.parent.parent
docs=[P/'monday_close_update_20261024.html',P.parent/'stock_deep_dive_risk_20261024.html',*sorted((P.parent/'stocks').glob('*.html')),root/'2026-10-23/global_market_positioning_20261026.html']
assert len(docs)==18
count=0
for path in docs:
    text=path.read_text(encoding='utf-8'); scan=Scan();scan.feed(text)
    assert len(scan.ids)==len(set(scan.ids)) and '\ufffd' not in text
    for url in scan.links:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        assert target.exists(),(str(path),url)
        if u.fragment and target.suffix=='.html':
            ts=Scan();ts.feed(target.read_text(encoding='utf-8'))
            assert unquote(u.fragment) in ts.ids,(str(path),url)
        count+=1
out={'passed':True,'session':'2026-10-23 regular-session quote snapshot','prices':260,'returns':259,'instruments':48,'models_checked':len(A['models']),'html_pages':len(docs),'local_links':count,'independent_weighted_return_volatility':independent,'all_stresses_independently_summed':True,'independent_recession_fixture':True,'beta_direct_regression_checked':True,'single_previous_close_conflict':'PG 0.005 dollars explicitly retained and sensitivity checked','cash_permission':'user confirmed','visual_qa':'pending','calculator_browser_check':'pending','sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in docs}}
(P/'validation_close.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['sha256','independent_weighted_return_volatility']},ensure_ascii=True))
