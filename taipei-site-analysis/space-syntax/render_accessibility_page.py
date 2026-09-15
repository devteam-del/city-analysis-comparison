"""Interactive A/B OD analysis over closed network envelopes. Uses already calculated routes."""
route_display=[{'case':r['case'],'origin':r['origin'],'destination':r['destination'],'distance':round(r['horizontal_m'],2),'points':line([positions[k] for k in r['keys']])} for r in routes]
point_display=[{'id':s['id'],'label':str(i+1),'name':s.get('name',s['id']),'side':s['side'],'xy':P(positions[s['node']])} for i,s in enumerate(samples)]
payload=json.dumps({'routes':route_display,'points':point_display,'rows':rows},ensure_ascii=False,separators=(',',':'))
svg_a=(OUT/'A.svg').read_text();svg_b=(OUT/'B.svg').read_text()
css='''body{margin:0;background:#f2f1eb;color:#253c35;font:16px/1.6 system-ui}header,main{padding:24px 3vw}header{border-bottom:1px solid #cdd5cf}h1{margin:0;font-size:28px}a{color:#356b63}.toolbar{display:flex;gap:18px;flex-wrap:wrap;align-items:center;margin:16px 0}select,button{font:inherit;padding:6px 12px;background:#fff;border:1px solid #a7b8ae;border-radius:4px}.maps{display:grid;grid-template-columns:1fr 1fr;gap:20px}.map svg{width:100%;height:auto;display:block}.map h2{font-size:18px}.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:14px}.swatch{display:inline-block;width:16px;height:12px;margin-right:5px}.notice{font-size:14px;max-width:1000px}.numbers{display:flex;gap:24px;flex-wrap:wrap;margin:12px 0}.numbers strong{font-size:28px}.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%;max-width:900px}td,th{padding:8px 18px;border-bottom:1px solid #cdd5cf;text-align:left}.downloads{display:flex;gap:16px;flex-wrap:wrap}@media(max-width:850px){.maps{grid-template-columns:1fr}header,main{padding:16px}}'''
script='''const data=JSON.parse(document.getElementById('data').textContent);
const origin=document.getElementById('origin'),radius=document.getElementById('radius'),show=document.getElementById('analysis');
const ns='http://www.w3.org/2000/svg';
for(const svg of document.querySelectorAll('.map svg')){
 svg.querySelectorAll('polyline,circle').forEach(e=>e.remove());
 svg.querySelectorAll('text').forEach(e=>{if(e.textContent!=='200 m')e.remove()});
 const g=document.createElementNS(ns,'g');g.id='analysis-overlay';svg.appendChild(g);
}
function update(){
 const id=origin.value,limit=Number(radius.value);let counts={};
 for(const c of ['A','B']){
  const svg=document.querySelector('#map'+c+' svg'),g=svg.querySelector('#analysis-overlay');g.innerHTML='';g.style.display=show.checked?'':'none';
  const routes=data.routes.filter(r=>r.case===c&&r.origin===id);counts[c]=routes.filter(r=>r.distance<=limit).length;
  for(const r of routes.filter(r=>r.distance<=limit)){
   const path=document.createElementNS(ns,'polyline');path.setAttribute('points',r.points);path.setAttribute('fill','none');path.setAttribute('stroke',c==='A'?'#ae623e':'#335d75');path.setAttribute('stroke-width','3');path.setAttribute('stroke-opacity','.68');g.appendChild(path);
  }
  for(const p of data.points){
   const r=routes.find(r=>r.destination===p.id);const selected=p.id===id;const active=r&&r.distance<=limit;
   const circle=document.createElementNS(ns,'circle');circle.setAttribute('cx',p.xy[0]);circle.setAttribute('cy',p.xy[1]);circle.setAttribute('r',selected?7:5);circle.setAttribute('fill',selected?'#172e28':active?'#ae623e':'#f2f1eb');circle.setAttribute('stroke','#52665c');g.appendChild(circle);
   const label=document.createElementNS(ns,'text');label.setAttribute('x',p.xy[0]+9);label.setAttribute('y',p.xy[1]-6);label.setAttribute('font-size','14');label.setAttribute('fill','#263c33');label.textContent=p.label;const title=document.createElementNS(ns,'title');title.textContent=p.name+' ('+p.id+')';circle.appendChild(title);g.appendChild(label);
  }
 }
 document.getElementById('countA').textContent=counts.A+'/'+data.points.filter(p=>p.side==='S').length;document.getElementById('countB').textContent=counts.B+'/'+data.points.filter(p=>p.side==='S').length;
 document.getElementById('scope').textContent=id+' 出發 · '+limit+' m 內的南側目的點';
 const rows=data.rows.filter(r=>r.origin===id);const name=x=>data.points.find(p=>p.id===x)?.name||x;
 document.getElementById('values').innerHTML=rows.map(r=>'<tr><td>'+name(r.destination)+'</td><td>'+(r.A_horizontal_m===null?'未接通':Math.round(r.A_horizontal_m))+'</td><td>'+(r.B_horizontal_m===null?'未接通':Math.round(r.B_horizontal_m))+'</td><td>'+(r.shorter_by_m===null?'—':Math.round(r.shorter_by_m))+'</td></tr>').join('');
}
for(const e of [origin,radius,show])e.addEventListener('change',update);
for(const c of ['A','B'])document.getElementById('export'+c).addEventListener('click',()=>{
 const svg=document.querySelector('#map'+c+' svg');const blob=new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=c+'-'+origin.value+'-'+radius.value+'m.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});update();'''
(OUT/'analysis-ui.js').write_text(script)
page='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>市民大道｜封閉路網與可達性</title><style>'''+css+'''</style><header><a href="../index.html">← 市民大道路網核對</a><h1>道路＋步行空間</h1><div class="legend"><span><i class="swatch" style="background:#dde1df"></i>道路面</span><span><i class="swatch" style="background:#a8beb4"></i>步行面</span><span><i class="swatch" style="background:#7dabbc"></i>天橋</span><span>實心點：門檻內可達目的點</span></div></header><main><div class="toolbar"><label>起點 <select id="origin">'''+''.join('<option'+(' selected' if s==north[0] else '')+' value="'+s['id']+'">'+html.escape(s.get('name',s['id']))+'</option>' for s in north)+'''</select></label><label>距離 <select id="radius"><option value="400">400 m</option><option value="800" selected>800 m</option><option value="1600">1,600 m</option></select></label><label><input id="analysis" type="checkbox" checked>顯示分析</label><button id="exportA">匯出目前 A 向量圖</button><button id="exportB">匯出目前 B 向量圖</button></div><div id="scope"></div><div class="numbers"><span>A 可達 <strong id="countA"></strong></span><span>B 可達 <strong id="countB"></strong></span></div><div class="maps"><section class="map" id="mapA"><h2>A｜地面步行網</h2>'''+svg_a+'''</section><section class="map" id="mapB"><h2>B｜地面＋承德市民天橋</h2>'''+svg_b+'''</section></div><p class="notice">線條顯示所選起點至門檻內目的點的最短路徑，不是完整等時圈。外緣為資料寬度與推定寬度形成的封閉面；缺步道寬度處以2 m表現，並非實測路緣。灰色道路不代表都可步行，封閉面合併不會新增模型接線。</p><div class="tablewrap"><table><thead><tr><th>目的點</th><th>A 距離（m）</th><th>B 距離（m）</th><th>少走（m）</th></tr></thead><tbody id="values"></tbody></table></div><p class="notice">交通與商業節點已替換原16點，包含善導寺。未接通項目另列；不作人流加權。部分商業點為街面代表位置，非測量門位。距離未計爬升與等待，B尚未納入地下通道。數值是條件式路網試算，不是實測人流或完整Space Syntax指標。</p><div class="downloads"><a href="selected-od-audit.json">新節點接線核對</a><a href="sample-points.json">全部新節點位置與名稱</a><a href="REPLACEMENT_REPORT.md">替換結果與缺口</a><a href="FOUR_POINT_VERIFICATION.md">歷史街景查核</a><a href="surface-width-audit.json">外緣寬度依據</a><a href="od-comparison.csv">全部數值</a><a href="A.svg">A 靜態向量圖（新選點）</a><a href="B.svg">B 靜態向量圖（新選點）</a></div><script id="data" type="application/json">'''+payload+'''</script><script>'''+script+'''</script></main></html>'''
(OUT/'index.html').write_text(page)
