from pathlib import Path
import urllib.request,urllib.parse,json,datetime
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
def fetch(t):
    start=int(datetime.datetime(2025,10,1,tzinfo=datetime.timezone.utc).timestamp())
    end=int(datetime.datetime(2026,10,24,tzinfo=datetime.timezone.utc).timestamp())
    url='https://query2.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(t)+'?'+urllib.parse.urlencode({'period1':start,'period2':end,'interval':'1d','events':'div,splits'})
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=18) as r:data=json.load(r)
        (P/'data'/('yahoo_probe_'+t+'.json')).write_text(json.dumps({'url':url,'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'response':data},ensure_ascii=False),encoding='utf-8')
        d=data['chart']['result'][0]
        return {'ticker':t,'n':len(d.get('timestamp',[])),'last_timestamp':d.get('timestamp',[])[-1:],'meta_regular_time':d['meta'].get('regularMarketTime'),'last_close':d['indicators']['quote'][0]['close'][-1:]}
    except Exception as e:return {'ticker':t,'error':str(e)}
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as ex: print(json.dumps(list(ex.map(fetch,['NVDA','AAPL'])),ensure_ascii=True))
