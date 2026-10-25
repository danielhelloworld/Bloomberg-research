from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,math,hashlib,datetime,re
P=Path(__file__).resolve().parent
A=json.loads((P/'attack_research.json').read_text(encoding='utf-8'))
(P/'validation.json').write_text('{"passed":false,"status":"running"}',encoding='utf-8')
assert len(A['stocks'])==len(A['metrics'])==28 and len(A['new_tickers'])==16 and len(A['retained_tickers'])==12
assert A['coverage']['combined_unique_companies_across_reports']==71
ids=[s['id'] for s in A['sources']];assert len(ids)==len(set(ids))
for t,s in A['stocks'].items():
    assert t==s['ticker'] and len(s['facts'])>=2
    for x in s['facts']:assert x['source_id'] in ids and x['claim']
    assert set(s['source_ids'])<=set(ids)
    assert s['trigger'] and s['kill'] and s['cash_quality']
    assert ('attack_case' in s or 'rebound_case' in s)
for source in A['sources']:
    date=source.get('published')
    if isinstance(date,str) and re.fullmatch(r'2026-\d\d-\d\d',date):assert date<='2026-10-25',(source['id'],date)
read=lambda i:json.loads(json.loads((P/'data'/f'snapshot_{i}.json').read_text(encoding='utf-8'))['content'][0]['text'])
quotes=read(0);calc=read(1)
assert len(quotes)==len(calc)==16
for q in quotes:
    t=q['symbol'].removesuffix('.US');m=A['metrics'][t]
    assert math.isclose(m['close'],float(q['last_done']))
    expected=(float(q['last_done'])-float(q['prev_close']))/float(q['prev_close'])*100
    assert math.isclose(m['r1'],expected,abs_tol=1e-10)
    assert float(q['low'])<=m['close']<=float(q['high']) and float(q['turnover'])>0
    assert q['timestamp'].startswith('2026-10-23T20:00:0')
    for key in ['rsi14','atr14','beta']:assert m[key] is None
for x in calc:
    t=x['symbol'].removesuffix('.US');m=A['metrics'][t]
    assert math.isclose(m['r5'],float(x['five_day_change_rate']))
    assert math.isclose(m['r10'],float(x['ten_day_change_rate']))
    assert abs(m['close']-float(x['last_done']))<=.011
reference_core={'XOM':5,'CVX':3,'JNJ':5,'ABBV':3,'PG':7,'WMT':3,'JPM':6,'BRK.B':6,'LMT':4}
shock={'XOM':-25,'CVX':-25,'JNJ':-12,'ABBV':-15,'PG':-10,'WMT':-14,'JPM':-28,'BRK.B':-18,'LMT':-15}
assert sum(reference_core.values())==42
core_loss=sum(reference_core[t]/100*shock[t] for t in reference_core)
assert math.isclose(core_loss,-7.53,abs_tol=1e-10)
for name,m in A['models'].items():
    assert m['reference_core']==reference_core
    attack=sum(m['attack'].values());assert math.isclose(attack,m['attack_pct']) and 0<attack<=8
    assert math.isclose(42+attack+m['cash_pct'],100)
    assert max(m['attack'].values())<=2
    loss=sum(w/100*m['shock_assumptions_pct'][t] for t,w in m['attack'].items())
    assert math.isclose(loss,m['attack_scenario_impact_pct'],abs_tol=1e-10)
    assert math.isclose(core_loss+loss,m['combined_with_core_recession_pct'],abs_tol=1e-10)
    assert math.isclose(core_loss-attack*.7,m['all_attack_down70_combined_pct'],abs_tol=1e-10)
    assert not set(m['attack'])&{'RKLB','MSTR','CRWV','NBIS','TEM','HIMS'}
assert math.isclose(A['models']['盈利兑现型']['attack_scenario_impact_pct'],-2.525,abs_tol=1e-10)
assert math.isclose(A['models']['高增长验证型']['combined_with_core_recession_pct'],-10.93,abs_tol=1e-10)
assert math.isclose(A['models']['高风险主题观察型']['combined_with_core_recession_pct'],-8.7425,abs_tol=1e-10)
events=json.loads((P/'attack_events.json').read_text(encoding='utf-8'))
for e in events:
    assert '2026-10-26'<=e['date_et']<='2026-10-30' and e['source_id'] in ids
    found=re.search(r'(\d{1,2}:\d{2})',str(e['time_et']))
    if found:
        dt=datetime.datetime.fromisoformat(e['date_et']+'T'+found.group(1).zfill(5))+datetime.timedelta(hours=12)
        assert e['beijing_reference']==dt.strftime('%m/%d %H:%M')
assert not set(e['ticker'] for e in events)&{'WDC','TSLA','RKLB','TEM','HIMS','ALAB'}
assert next(e for e in events if e['ticker']=='STX')['date_et']=='2026-10-27'
assert next(e for e in events if e['ticker']=='GEV')['beijing_reference']=='10/28 19:30'
assert next(e for e in events if e['ticker']=='SNDK')['beijing_reference']=='10/30 04:30'
class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:self.ids.append(a['id'])
        if tag=='a'and 'href'in a:self.links.append(a['href'])
docs=[P/'aggressive_equity_20261025.html',P/'sources.html',*sorted((P/'stocks').glob('*.html'))]
assert len(docs)==30
count=0
for p in docs:
    raw=p.read_text(encoding='utf-8');s=Scan();s.feed(raw)
    assert '\ufffd' not in raw and '根代理' not in raw
    assert len(s.ids)==len(set(s.ids)),p
    for url in s.links:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        target=(p.parent/unquote(u.path)).resolve() if u.path else p
        assert target.exists(),(p,url)
        if u.fragment and target.suffix=='.html':
            y=Scan();y.feed(target.read_text(encoding='utf-8'));assert unquote(u.fragment) in y.ids,(p,url)
        count+=1
main=(P/'aggressive_equity_20261025.html').read_text(encoding='utf-8')
assert '2027' in main and '13.13%' in main and '125%' in main
assert A['constraints']['max_single_pct_user']==20 and 'User explicitly confirms' in A['constraints']['cash_rules']
out={'passed':True,'stock_pages':28,'new_companies':16,'combined_unique_company_coverage':71,'source_records':len(ids),'unique_source_urls':len(set(s['url'] for s in A['sources'])),'html_pages':30,'local_links_checked':count,'quote_rows':16,'all_dates_regular_session':'2026-10-23','independent_scenario_arithmetic':True,'model_weights_sum_to100':True,'RKLB_and_funding_gated_names_excluded_from_examples':True,'next_week_event_rows':len(events),'event_timezone_conversions_checked':True,'RSI_ATR_beta_missing_not_fabricated':True,'visual_qa':'pending','calculator_browser_qa':'pending','sha256':{str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in docs}}
(P/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='sha256'},ensure_ascii=True))
