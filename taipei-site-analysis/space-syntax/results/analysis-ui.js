const data=JSON.parse(document.getElementById('data').textContent);
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
   const label=document.createElementNS(ns,'text');label.setAttribute('x',p.xy[0]+9);label.setAttribute('y',p.xy[1]-6);label.setAttribute('font-size','14');label.setAttribute('fill','#263c33');label.textContent=p.id;g.appendChild(label);
  }
 }
 document.getElementById('countA').textContent=counts.A+'/8';document.getElementById('countB').textContent=counts.B+'/8';
 document.getElementById('scope').textContent=id+' 出發 · '+limit+' m 內的南側目的點';
 const rows=data.rows.filter(r=>r.origin===id);
 document.getElementById('values').innerHTML=rows.map(r=>'<tr><td>'+r.destination+'</td><td>'+Math.round(r.A_horizontal_m)+'</td><td>'+Math.round(r.B_horizontal_m)+'</td><td>'+Math.round(r.shorter_by_m)+'</td></tr>').join('');
}
for(const e of [origin,radius,show])e.addEventListener('change',update);
for(const c of ['A','B'])document.getElementById('export'+c).addEventListener('click',()=>{
 const svg=document.querySelector('#map'+c+' svg');const blob=new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=c+'-'+origin.value+'-'+radius.value+'m.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});update();