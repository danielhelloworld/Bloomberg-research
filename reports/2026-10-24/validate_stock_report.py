from pathlib import Path
import json,re,math,hashlib
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
r=json.loads((P/'risk_comparison.json').read_text(encoding='utf-8'))
if not (P/'validation.json').exists():
 (P/'validation.json').write_text('{"passed":false,"status":"validation running"}',encoding='utf-8')
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if tag=='a'and 'href'in a:self.links.append(a['href'])
files=[P/'stock_deep_dive_risk_20261024.html',*sorted((P/'stocks').glob('*.html'))]
errors=[];local_links=0
for f in files:
 text=f.read_text(encoding='utf-8');x=Scan();x.feed(text)
 assert '\ufffd' not in text,f'Unicode replacement in {f}'
 assert len(x.ids)==len(set(x.ids)),f'Duplicate IDs {f}'
 for url in x.links:
  z=urlsplit(url)
  if z.scheme or z.netloc:continue
  target=(f.parent/unquote(z.path)).resolve() if z.path else f
  if not target.exists():errors.append(f'{f.name}: missing {url}');continue
  if z.fragment and target.suffix=='.html':
   y=Scan();y.feed(target.read_text(encoding='utf-8'))
   if unquote(z.fragment) not in y.ids:errors.append(f'{f.name}: invalid fragment {url}')
  local_links+=1
assert len(files)==16
assert not errors,errors
for name,w in r['models'].items():
 assert math.isclose(sum(w.values()),100,abs_tol=1e-8)
 assert all(v>=0 for v in w.values())
 assert max(v for s,v in w.items() if s!='CASH')<=20
 for label,shock in r['stress_vectors'].items():
  # Explicit sum of dollars lost per $100 NAV, separate from risk_analysis loop.
  expected=sum(w.get(s,0)/100*shock.get(s,0) for s in w if s!='CASH')
  assert math.isclose(expected,r['risk'][name]['scenario'][label],abs_tol=1e-10)
 assert sum(v>0 for s,v in w.items() if s!='CASH') in [8,11,15]
# Independent covariance calculation for target 50% using return matrix multiplication.
old=P.parent/'2026-10-23'
history=json.loads((old/'stock_raw.json').read_text())['history']
sy=[s for s,v in r['models']['修订B_50'].items() if s!='CASH' and v>0]
px=pd.DataFrame({s:pd.Series({t[:10]:float(v) for t,v,vol in history[s] if t[:10]<'2026-10-23'}) for s in sy})
ret=np.log(px/px.shift()).dropna().tail(60);X=ret.to_numpy();X=X-X.mean(axis=0)
w=np.array([r['models']['修订B_50'][s]/100 for s in sy])
direct=np.std(X@w,ddof=1)*math.sqrt(252)*100
assert math.isclose(direct,r['risk']['修订B_50']['windows']['60']['vol'],abs_tol=1e-10)
sources=json.loads((P/'source_register.json').read_text(encoding='utf-8'))
stockdocs=json.loads((P/'stock_research_synthesis.json').read_text(encoding='utf-8'))['stocks']
assert len(stockdocs)==15 and len(sources)>=40
assert r['user_constraints']['max_drawdown_tolerance_pct']==12
assert r['user_constraints']['initial_entry_completed']=='user confirmed'
out={'passed':True,'html_pages':len(files),'local_links_checked':local_links,'unique_primary_source_urls':len(sources),'stock_coverage':list(stockdocs),'all_weights_total_100':True,'long_only_and_max_single_20_pass':True,'scenario_arithmetic_independently_checked':True,'independent_60_day_vol_pct':direct,'return_rows_60':len(ret),'last_complete_price':str(px.index[-1]),'user_drawdown_tolerance_pct':12,'visual_qa':'pending browser review','sha256':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(P/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='sha256'},ensure_ascii=False))
