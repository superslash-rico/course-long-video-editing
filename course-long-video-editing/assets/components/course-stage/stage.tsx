import React from 'react';
import {AbsoluteFill,useVideoConfig} from 'remotion';
import {backgroundDefaults} from './background';
import {cameraTransform} from './camera';
import {SourceCredit} from './source-credit';

export function CourseBackground({camera,values={},id='course-background'}:any){
 const {width,height}=useVideoConfig(),p={...backgroundDefaults,...values},u=height/1080;
 if(p.transparentBackground)return null;
 const ratio=Math.max(.02,camera?.s??.77)/.77,z=1+.45*Math.tanh(Math.log(ratio)*p.dotZoomStrength),spacing=Math.max(18,p.dotSpacing*z)*u,hz=1+(z-1)*.25,x=camera?.fx??0,y=camera?.fy??0;
 return <AbsoluteFill style={{zIndex:0,background:p.backgroundColor,pointerEvents:'none'}}><svg width={width} height={height}>
  <defs><pattern id={id+'-dots'} width={spacing} height={spacing} x={width*.5*(1-z)-x*u*p.dotParallaxStrength} y={height*.5*(1-z)-y*u*p.dotParallaxStrength} patternUnits="userSpaceOnUse"><circle cx={spacing/2} cy={spacing/2} r={Math.max(.45,p.dotRadius*z)*u} fill={p.dotColor}/></pattern><radialGradient id={id+'-halo'}><stop offset="0%" stopColor="#EBD9F3"/><stop offset="30%" stopColor={p.haloColor} stopOpacity=".68"/><stop offset="68%" stopColor={p.haloColor} stopOpacity=".22"/><stop offset="100%" stopColor={p.haloColor} stopOpacity="0"/></radialGradient></defs>
  <g transform={`translate(${width/2-x*u*p.dotParallaxStrength*.08} ${height/2-y*u*p.dotParallaxStrength*.08}) scale(${hz}) translate(${-width/2} ${-height/2})`}>{[[.5,.5,1.56,1,.55],[.5,.495,1.46,.48,1],[.281,.478,.885,.28,.30],[.766,.51,.865,.32,.28]].map(([cx,cy,rx,ry,a],i)=><ellipse key={i} cx={cx*width} cy={cy*height} rx={rx*width} ry={ry*p.haloHeight*u} fill={`url(#${id}-halo)`} opacity={a*p.haloOpacity}/>)}</g><rect width={width} height={height} fill={`url(#${id}-dots)`} opacity={p.dotOpacity}/>
 </svg></AbsoluteFill>;
}

export function CameraStage({camera,children,x=755,y=540}:any){
 const {height}=useVideoConfig(),unit=height/1080;
 return <AbsoluteFill style={{zIndex:10,isolation:'isolate'}}><div style={{position:'absolute',inset:0,transform:`scale(${unit})`,transformOrigin:'0 0'}}><div style={{position:'absolute',left:x,top:y,width:1,height:1,perspective:2500,perspectiveOrigin:'0 0',transformStyle:'preserve-3d'}}><div style={{position:'absolute',width:1,height:1,transformOrigin:'0 0',transformStyle:'preserve-3d',transform:cameraTransform(camera)}}>{children}</div></div></div></AbsoluteFill>;
}

export function OpaquePaper({children,x=0,y=0,z=0,width=600,height=500,rotation=0,tone=1,contentOpacity=1,reveal=1,paperColor='#FBF7FD',inkColor='#24182D'}:any){
 return <div style={{position:'absolute',left:x-width/2,top:y-height/2,width,height,transformStyle:'preserve-3d',transform:`translateZ(${z}px) rotateZ(${rotation}deg)`,opacity:reveal}}><div style={{position:'absolute',inset:-5,borderRadius:8,background:'rgba(25,10,34,.50)',filter:'blur(15px)',transform:'translate3d(7px,10px,-18px)'}}/>{[9,6,3].map((d,i)=><div key={d} style={{position:'absolute',inset:0,borderRadius:6,background:['#CBB7D8','#DDD0E5','#EEE5F3'][i],transform:`translate3d(${-i}px,${i}px,${-d}px)`}}/>)}<div style={{position:'absolute',inset:0,background:paperColor,color:inkColor,borderRadius:6,backfaceVisibility:'hidden',boxShadow:'inset 0 0 0 1px #E0D3E8',filter:tone<1?`brightness(${Math.max(.1,tone)})`:undefined}}><div style={{position:'absolute',inset:0,opacity:contentOpacity}}>{children}</div></div></div>;
}

// Preferred root: the exact same camera drives the backdrop AND foreground.
export function CourseWorld({camera,values={},children,x=755,y=540,id='course-world',sourceNote,sourceCreditOpacity=1}:any){return <AbsoluteFill><CourseBackground camera={camera} values={values} id={id}/><CameraStage camera={camera} x={x} y={y}>{children}</CameraStage><SourceCredit text={sourceNote??values.sourceNote} fontFamily={values.font} opacity={sourceCreditOpacity}/></AbsoluteFill>;}
