(()=>{
 const tabs=[...document.querySelectorAll('[data-map]')],panels=[...document.querySelectorAll('.map-panel')];
 const zoom=document.getElementById('mapzoom'),out=document.getElementById('zoomvalue');
 function select(tab){
  const active=panels.find(p=>!p.hidden),view=active?.querySelector('.mapscroll');
  const ratio=view&&view.scrollWidth>view.clientWidth?view.scrollLeft/(view.scrollWidth-view.clientWidth):0;
  tabs.forEach(t=>{const selected=t===tab;t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;document.getElementById(t.getAttribute('aria-controls')).hidden=!selected;});
  const next=document.getElementById(tab.getAttribute('aria-controls')).querySelector('.mapscroll');next.scrollLeft=ratio*Math.max(0,next.scrollWidth-next.clientWidth);
 }
 tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>select(tab));tab.addEventListener('keydown',e=>{let j;if(e.key==='ArrowRight')j=(i+1)%tabs.length;if(e.key==='ArrowLeft')j=(i+tabs.length-1)%tabs.length;if(e.key==='Home')j=0;if(e.key==='End')j=tabs.length-1;if(j!==undefined){e.preventDefault();select(tabs[j]);tabs[j].focus();}});});
 function scale(){const value=Number(zoom.value);out.value=value+'×';document.querySelectorAll('.mapscroll img').forEach(img=>{img.style.width=value*100+'%';img.style.minWidth=1300*value+'px';});}
 zoom.addEventListener('input',scale);document.getElementById('resetzoom').addEventListener('click',()=>{zoom.value='1';scale();document.querySelectorAll('.mapscroll').forEach(el=>el.scrollLeft=0);});
})();
