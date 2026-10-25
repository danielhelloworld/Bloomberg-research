from pathlib import Path
import json,zipfile,hashlib,datetime
P=Path(__file__).resolve().parent
root=P.parent.parent
validation=json.loads((P/'validation_close.json').read_text(encoding='utf-8'))
assert validation['passed']
assert validation['visual_qa']=='passed desktop opening, allocations, risk table and individual-stock section via local HTTP browser'
assert validation['calculator_browser_check']=='passed default 1m starter, 2m target and invalid zero NAV; restored default'
oldzip=root/'stock_deep_dive_risk_20261024.zip'
with zipfile.ZipFile(oldzip) as z:
    basepaths=[root/name for name in z.namelist() if not name.endswith('/')]
paths=sorted(set(basepaths+list(P.glob('*'))))
paths=[p for p in paths if p.is_file() and p.name not in ['package_manifest.json']]
manifest={'built_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entry':'2026-10-24/closing_update/monday_close_update_20261024.html','files':{str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'validation':'2026-10-24/closing_update/validation_close.json','no_trades_executed':True}
(P/'package_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
paths.append(P/'package_manifest.json')
out=root/'stock_deep_dive_risk_20261024_close.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,str(p.relative_to(root)))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(paths)==len(set(z.namelist()))
    for name,digest in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'files':len(paths),'manifest_sha256_verified':True},ensure_ascii=True))
