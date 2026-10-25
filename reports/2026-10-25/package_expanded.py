from pathlib import Path
import json,zipfile,hashlib,datetime
P=Path(__file__).resolve().parent
ROOT=P.parent
v=json.loads((P/'validation.json').read_text(encoding='utf-8'))
assert v['passed'] and v['visual_qa'].startswith('passed') and v['browser_interaction_qa'].startswith('passed')
previous=ROOT/'stock_deep_dive_risk_20261024_close.zip'
files={}
with zipfile.ZipFile(previous) as z:
    for name in z.namelist():
        if not name.endswith('/'):files[name]=z.read(name)
for p in sorted(P.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.name!='package_manifest.json':files[str(p.relative_to(ROOT)).replace('\\','/')]=p.read_bytes()
manifest={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entry':'2026-10-25/weekly_expanded_20261026_30.html','coverage':{'stocks':55,'additional':40,'daily_previews':5,'ticker_day_rows':60},'prior_package':'stock_deep_dive_risk_20261024_close.zip','no_trades_executed':True,'daily_previews_are_not_future_observed_results':True,'sha256':{name:hashlib.sha256(raw).hexdigest() for name,raw in sorted(files.items())}}
(P/'package_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
files['2026-10-25/package_manifest.json']=(P/'package_manifest.json').read_bytes()
dest=ROOT/'expanded_equity_week_20261026_30.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for name,raw in sorted(files.items()):z.writestr(name,raw)
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None and len(z.namelist())==len(files)
    for name,digest in manifest['sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps({'zip':str(dest),'files':len(files),'bytes':dest.stat().st_size,'all_hashes_verified':True},ensure_ascii=True))
