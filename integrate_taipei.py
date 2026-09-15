from pathlib import Path
ROOT=Path(__file__).resolve().parent
entry='''<nav id="research-sections" aria-label="研究分區" style="display:flex;gap:28px;flex-wrap:wrap;max-width:1440px;margin:0 auto;padding:18px 24px;border-block:1px solid #ccd2c7"><a href="#workspace">國際案例對照</a><a class="taipei-entry" href="taipei-site-analysis/index.html" style="font-weight:700;color:#536d56">市民大道｜基地診斷 →</a></nav><script>if(location.pathname.includes('/dist/'))document.querySelectorAll('.taipei-entry').forEach(a=>a.setAttribute('href','../taipei-site-analysis/index.html'));</script>'''
for name in ['site-v2-body.html','site-template.html','urban-history-comparison.html','dist/index.html']:
 p=ROOT/name;s=p.read_text()
 if 'id="research-sections"' not in s:
  assert '<main id="workspace">' in s,name
  p.write_text(s.replace('<main id="workspace">',entry+'\n<main id="workspace">',1))
 print('Integrated',name)
