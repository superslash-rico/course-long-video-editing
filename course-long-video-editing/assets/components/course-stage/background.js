// Adapted from the confirmed course background; no course media or project IDs.
export const backgroundDefaults={backgroundColor:'#0C0A14',dotColor:'#B4A7C4',dotOpacity:.42,dotSpacing:42,dotRadius:1.6,dotZoomStrength:.55,dotParallaxStrength:.025,haloColor:'#B989D2',haloOpacity:.18,haloHeight:220,transparentBackground:false};
const NS='http://www.w3.org/2000/svg';
export function createBackground(host,{width=1920,height=1080,id='course-bg'}={}){
 const doc=host.ownerDocument,svg=doc.createElementNS(NS,'svg');
 svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
 Object.assign(svg.style,{position:'absolute',inset:'0',width:'100%',height:'100%',zIndex:'0',pointerEvents:'none'});
 const node=(tag,attrs,parent)=>{const n=doc.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,String(v));parent.append(n);return n;};
 const defs=node('defs',{},svg),pattern=node('pattern',{id:id+'-dots',patternUnits:'userSpaceOnUse'},defs),dot=node('circle',{},pattern);
 const halo=node('radialGradient',{id:id+'-halo'},defs);const stops=[];
 for(const[o,a]of[['0%','1'],['30%','.68'],['68%','.22'],['100%','0']])stops.push(node('stop',{offset:o,'stop-opacity':a},halo));
 const base=node('rect',{width,height},svg),cloud=node('g',{},svg);
 const ellipses=[[.5,.5,1.56,1,.55],[.5,.495,1.46,.48,1],[.281,.478,.885,.28,.30],[.766,.51,.865,.32,.28]].map(([cx,cy,rx,ry,opacity])=>({el:node('ellipse',{cx:cx*width,cy:cy*height,rx:rx*width,fill:`url(#${id}-halo)`},cloud),ry,opacity}));
 const field=node('rect',{width,height,fill:`url(#${id}-dots)`},svg);host.prepend(svg);
 return{element:svg,render(values,camera={s:1,fx:0,fy:0},referenceScale=.77){
  const p={...backgroundDefaults,...values},unit=height/1080;
  svg.style.display=p.transparentBackground?'none':'';base.setAttribute('fill',p.backgroundColor);
  const z=1+.45*Math.tanh(Math.log(Math.max(.02,camera.s)/referenceScale)*p.dotZoomStrength),spacing=Math.max(18,p.dotSpacing*z)*unit;
  pattern.setAttribute('width',spacing);pattern.setAttribute('height',spacing);pattern.setAttribute('x',width*.5*(1-z)-camera.fx*unit*p.dotParallaxStrength);pattern.setAttribute('y',height*.5*(1-z)-camera.fy*unit*p.dotParallaxStrength);
  dot.setAttribute('cx',spacing/2);dot.setAttribute('cy',spacing/2);dot.setAttribute('r',Math.max(.45,p.dotRadius*z)*unit);dot.setAttribute('fill',p.dotColor);field.setAttribute('opacity',p.dotOpacity);
  stops.forEach((n,i)=>n.setAttribute('stop-color',i===0?'#EBD9F3':p.haloColor));
  const hz=1+(z-1)*.25;cloud.setAttribute('transform',`translate(${width/2-camera.fx*unit*p.dotParallaxStrength*.08} ${height/2-camera.fy*unit*p.dotParallaxStrength*.08}) scale(${hz}) translate(${-width/2} ${-height/2})`);
  ellipses.forEach(q=>{q.el.setAttribute('ry',p.haloHeight*unit*q.ry);q.el.setAttribute('opacity',p.haloOpacity*q.opacity);});
 },dispose(){svg.remove();}};
}
