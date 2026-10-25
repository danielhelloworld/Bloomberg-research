from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,csv,math,hashlib,re,datetime
P=Path(__file__).resolve().parent
A=json.loads((P/'expanded_research.json').read_text(encoding='utf-8'))
(P/'validation.json').write_text('{"passed":false,"status":"running"}',encoding='utf-8')
assert A['scope']=={'total':55,'legacy':15,'additional':40,'daily_previews':5,'per_day_names':12,'ticker_day_rows':60,'unique_daily_names':36}
assert len(A['metrics'])==55 and len(A['new_stocks'])==40 and len(A['legacy_stocks'])==15
ids=[s['id'] for s in A['sources']];assert len(ids)==len(set(ids))==124
assert len(set(s['url'] for s in A['sources']))==120
future_pub=[]
for s in A['sources']:
    v=s.get('published')
    if isinstance(v,str) and re.fullmatch(r'2026-\d\d-\d\d',v) and v>'2026-10-25':future_pub.append((s['id'],v))
assert not future_pub,future_pub
for t,s in A['new_stocks'].items():
    assert s['ticker']==t and len(s['facts'])>=2 and s['source_ids']
    for fact in s['facts']:assert fact['source_id'] in ids and fact['claim']
    assert set(s['source_ids'])<=set(ids)
    for key in ['guidance','cash_quality','rebound_case','trap_case','kill','trigger']:assert s[key]
q=json.loads(json.loads((P/'data/fetch_1.json').read_text(encoding='utf-8'))['content'][0]['text'])
ix=json.loads(json.loads((P/'data/fetch_2.json').read_text(encoding='utf-8'))['content'][0]['text'])
assert len(q)==55 and len(ix)==40
for x in q:
    t=x['symbol'].removesuffix('.US');m=A['metrics'][t]
    assert math.isclose(m['close'],float(x['last_done']))
    assert math.isclose(m['r1'],(float(x['last_done'])-float(x['prev_close']))/float(x['prev_close'])*100,abs_tol=1e-10)
    assert m['quote_timestamp'].startswith('2026-10-23T20:00:0') and m['volume_friday']>0
    assert m['rsi14'] is None and m['atr14'] is None and m['drawdown52w'] is None
bucket={'短期急跌待确认':0,'已反弹等待回踩':0,'温和回撤观察':0,'非超跌/强势对照':0}
for x in ix:
    t=x['symbol'].removesuffix('.US');m=A['metrics'][t]
    assert math.isclose(m['r5'],float(x['five_day_change_rate'])) and math.isclose(m['r10'],float(x['ten_day_change_rate']))
    assert abs(float(x['last_done'])-m['close'])<=.011
    r5=float(x['five_day_change_rate']);r10=float(x['ten_day_change_rate'])
    b='短期急跌待确认' if r10<=-10 and r5<=0 else '已反弹等待回踩' if r10<0 and r5>0 else '非超跌/强势对照' if r10>=0 else '温和回撤观察'
    assert m['price_bucket']==b;bucket[b]+=1
assert bucket==A['funnel']
assert [d['date'] for d in A['days']]==['2026-10-26','2026-10-27','2026-10-28','2026-10-29','2026-10-30']
for d in A['days']:
    assert len(d['names'])==len(set(d['names']))==12
    assert set(d['focus'])<=set(d['names']) and set(d['wait'])<=set(d['names'])
events=json.loads((P/'event_register.json').read_text(encoding='utf-8'))
assert len(events)==18
for ev in events:
    assert '2026-10-26'<=ev['date_et']<='2026-10-30' and ev['source_id'] in ids
    et=datetime.datetime.fromisoformat(ev['date_et']+'T'+ev['call_time_et'])
    assert (et+datetime.timedelta(hours=12)).strftime('%m/%d %H:%M')==ev['beijing_call']
assert not any(e['ticker'] in ['AAPL','META','NFLX','LRCX','ANET','MU'] for e in events)
assert next(e for e in events if e['ticker']=='NOW')['call_time_et']=='17:00'
assert next(e for e in events if e['ticker']=='MA')['release_window']=='精确首次发布时点未核'
ics=(P/'confirmed_events.ics').read_text(encoding='utf-8')
assert ics.count('BEGIN:VEVENT')==17 and 'GOOGL' not in ics
assert '20261028T210000Z' in ics # NOW and KLAC17:00ET =21:00UTC.
# Independent stress fixture using the nine non-tech reference holdings.
core={'XOM':(5,-25),'CVX':(3,-25),'JNJ':(5,-12),'ABBV':(3,-15),'PG':(7,-10),'WMT':(3,-14),'JPM':(6,-28),'BRK.B':(6,-18),'LMT':(4,-15)}
assert sum(w for w,v in core.values())==42
coreloss=sum(w*v/100 for w,v in core.values());assert math.isclose(coreloss,-7.53)
for r in A['replacement_stress']:
    assert math.isclose(r['core_equity_pct']+r['replacement_tech_pct']+r['cash_pct'],100)
    expected=coreloss+r['replacement_tech_pct']/100*r['tech_shock_pct']
    assert math.isclose(expected,r['combined_NAV_impact_pct'],abs_tol=1e-10)
assert math.isclose(A['replacement_stress'][-1]['combined_NAV_impact_pct'],-11.53)
class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.tr=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:self.ids.append(a['id'])
        if tag=='a'and 'href'in a:self.links.append(a['href'])
docs=[P/'weekly_expanded_20261026_30.html',P/'sources.html',*sorted((P/'days').glob('*.html')),*sorted((P/'stocks').glob('*.html'))]
assert len(docs)==62
local=0
for doc in docs:
    raw=doc.read_text(encoding='utf-8');s=Scan();s.feed(raw)
    assert '\ufffd' not in raw and len(s.ids)==len(set(s.ids)),doc
    for url in s.links:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        target=(doc.parent/unquote(u.path)).resolve() if u.path else doc
        assert target.exists(),(doc,url)
        if u.fragment and target.suffix=='.html':
            ts=Scan();ts.feed(target.read_text(encoding='utf-8'));assert unquote(u.fragment) in ts.ids,(doc,url)
        local+=1
for d in A['days']:
    doc=(P/'days'/f'day_{d["date"].replace("-","")}.html').read_text(encoding='utf-8')
    assert '事前预选，尚待当日刷新' in doc and '尚未发生' in doc
out={'passed':True,'stocks_total':55,'additional_stocks':40,'legacy_stocks':15,'daily_reports':5,'daily_rows':60,'unique_daily_candidates':36,'source_records':124,'unique_source_urls':120,'html_pages':62,'local_links_checked':local,'quote_session':'2026-10-23 regular session','price_bucket_independent_check':True,'source_references_resolve':True,'all_18_event_times_independently_converted':True,'confirmed_ics_events':17,'future_results_not_fabricated':True,'independent_core_stress_pct':coreloss,'independent_replacement_scenarios':True,'technical_fields_missing_are_null':True,'visual_qa':'pending','browser_interaction_qa':'pending','sha256':{str(doc.relative_to(P)):hashlib.sha256(doc.read_bytes()).hexdigest() for doc in docs}}
(P/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='sha256'},ensure_ascii=True))
