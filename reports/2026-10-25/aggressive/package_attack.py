from pathlib import Path
import json,zipfile,hashlib,datetime
P=Path(__file__).resolve().parent
ROOT=P.parent.parent
v=json.loads((P/'validation.json').read_text(encoding='utf-8'))
assert v['passed'] and v['visual_qa'].startswith('passed') and v['calculator_browser_qa'].startswith('passed')
files={}
with zipfile.ZipFile(ROOT/'expanded_equity_week_20261026_30.zip') as z:
    for name in z.namelist():
        if not name.endswith('/'):files[name]=z.read(name)
for p in P.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.name!='package_manifest.json':files[str(p.relative_to(ROOT)).replace('\\','/')]=p.read_bytes()
manifest={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entry':'2026-10-25/aggressive/aggressive_equity_20261025.html','coverage': {'attack_candidates':28,'new_companies':16,'combined_unique_companies':71},'prior_packet':'expanded_equity_week_20261026_30.zip','no_trades':True,'sha256':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}}
(P/'package_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
files['2026-10-25/aggressive/package_manifest.json']=(P/'package_manifest.json').read_bytes()
out=ROOT/'aggressive_equity_research_20261025.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for name,raw in sorted(files.items()):z.writestr(name,raw)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None and len(z.namelist())==len(files)
    for name,digest in manifest['sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps({'zip':str(out),'files':len(files),'bytes':out.stat().st_size,'all_hashes_verified':True},ensure_ascii=True))
