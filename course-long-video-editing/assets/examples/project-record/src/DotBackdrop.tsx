import React from 'react';
import {AbsoluteFill,useCurrentFrame,useVideoConfig} from 'remotion';
// Continuous far-field parallax from the real authored camera, not a second zoom clock.
export function dotView(p:any,cam:any={},seconds=0,originY=540){
 const base=Math.max(.05,Number(p.dotBaseScale));const raw=Math.max(.02,Number(cam.s??base));
 const zoom=p.dotCameraFollow?1+.45*Math.tanh(Math.log(raw/base)*Number(p.dotZoomStrength)):1;
 const driftX=p.dotDriftEnabled?1.8*Math.sin(seconds/18):0,driftY=p.dotDriftEnabled?1.2*Math.cos(seconds/23):0;
 const panX=p.dotCameraFollow?(cam.x!==undefined?-Number(cam.x)*p.dotParallaxStrength:Number(cam.cx??0)*p.dotParallaxStrength*10):0;
 const panY=p.dotCameraFollow?(cam.y!==undefined?-Number(cam.y)*p.dotParallaxStrength:Number(cam.cy??0)*p.dotParallaxStrength*10):0;
 return {zoom,spacing:Number(p.dotSpacing)*zoom,radius:Number(p.dotRadius)*zoom,x:960*(1-zoom)+panX+driftX,y:originY*(1-zoom)+panY+driftY,haloZoom:1+(zoom-1)*.25,haloX:panX*.08,haloY:panY*.08};
}
export function DotBackdrop({p,cam={},originY=540}:any){
 const frame=useCurrentFrame();const {fps}=useVideoConfig();const seconds=frame/fps;
 if(p.transparentBackground)return null;
 const v=dotView(p,cam,seconds,originY),s=Math.max(18,v.spacing),r=Math.max(.45,v.radius),id='ricoDots'+String(p.dotPatternKey),enabled=p.spaceBackgroundEnabled!==false;
 return <AbsoluteFill style={{background:p.backgroundColor}}>
  {enabled&&<svg width={1920} height={1080} style={{position:'absolute',inset:0}}>
   <defs>
    <pattern id={id+'Pattern'} x={v.x} y={v.y} width={s} height={s} patternUnits="userSpaceOnUse"><circle cx={s/2} cy={s/2} r={r} fill={p.dotColor}/></pattern>
    <radialGradient id={id+'Halo'}><stop offset="0%" stopColor="#EBD9F3" stopOpacity="1"/><stop offset="30%" stopColor={p.haloColor} stopOpacity=".68"/><stop offset="68%" stopColor={p.haloColor} stopOpacity=".22"/><stop offset="100%" stopColor={p.haloColor} stopOpacity="0"/></radialGradient>
    <radialGradient id={id+'Cloud'}><stop offset="0%" stopColor={p.haloColor} stopOpacity=".75"/><stop offset="60%" stopColor={p.haloColor} stopOpacity=".24"/><stop offset="100%" stopColor={p.haloColor} stopOpacity="0"/></radialGradient>
    <radialGradient id={id+'Edge'} cx="50%" cy="50%" r="82%"><stop offset="35%" stopColor={p.backgroundColor} stopOpacity="0"/><stop offset="100%" stopColor={p.backgroundColor} stopOpacity=".28"/></radialGradient>
   </defs>
   {p.haloEnabled&&<g transform={`translate(${960+v.haloX} ${540+v.haloY}) scale(${v.haloZoom}) translate(-960 -540)`}>
    <ellipse cx="960" cy="540" rx="1500" ry={p.haloHeight} fill={'url(#'+id+'Cloud)'} opacity={p.haloOpacity*.55}/>
    <ellipse cx="960" cy="535" rx="1400" ry={p.haloHeight*.48} fill={'url(#'+id+'Halo)'} opacity={p.haloOpacity}/>
    <ellipse cx="540" cy="516" rx="850" ry={p.haloHeight*.28} fill={'url(#'+id+'Cloud)'} opacity={p.haloOpacity*.3}/>
    <ellipse cx="1470" cy="551" rx="830" ry={p.haloHeight*.32} fill={'url(#'+id+'Cloud)'} opacity={p.haloOpacity*.28}/>
   </g>}
   <rect width="1920" height="1080" fill={'url(#'+id+'Pattern)'} opacity={p.dotOpacity}/>
   <rect width="1920" height="1080" fill={'url(#'+id+'Edge)'}/>
  </svg>}
 </AbsoluteFill>;
}
