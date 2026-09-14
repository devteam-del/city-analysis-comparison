"""Restore public-source PDFs locally; compare bytes with the research snapshot."""
from pathlib import Path
import hashlib,json,subprocess
base=Path(__file__).resolve().parent
for record in json.loads((base/'SOURCE_MANIFEST.json').read_text()):
    target=base/Path(record['path']).name
    if not target.exists():
        subprocess.run(['curl','--fail','--location','--max-time','60',record['url'],'--output',str(target)],check=True)
    actual=hashlib.sha256(target.read_bytes()).hexdigest()
    print(target.name, 'MATCH' if actual==record['sha256'] else 'SOURCE CHANGED: verify new version before use')
