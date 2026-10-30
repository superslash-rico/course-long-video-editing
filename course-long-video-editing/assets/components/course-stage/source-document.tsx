import React from 'react';
import {Img} from 'remotion';
import {OpaquePaper} from './stage';
import {phase} from './camera';
import {handMarkLayers} from './hand-marks';

// A real image and all its marks share the SAME source-pixel coordinate plane.
// src is supplied by the receiving project's actual media binding, never a demo ID.
export function SourceDocument({src,sourceWidth,sourceHeight,width=1280,x=0,y=0,z=96,timeSeconds=0,marks=[],tone=1,reveal=1}:any){
 if(!src||![sourceWidth,sourceHeight,width].every(v=>Number.isFinite(v)&&v>0))throw new Error('Bind a verified source image and its actual pixel dimensions');
 const unit=width/sourceWidth,height=sourceHeight*unit;
 return <OpaquePaper x={x} y={y} z={z} width={width} height={height} tone={tone} reveal={reveal}>
  <Img src={src} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/>
  <svg viewBox={`0 0 ${sourceWidth} ${sourceHeight}`} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
   {marks.map((m,i)=>{
    const layers=handMarkLayers(m,sourceWidth,sourceHeight,unit),p=phase(timeSeconds,m.at??0,(m.at??0)+(m.draw??.52));
    if(!p)return null;
    return <g key={i}>{layers.map((q,j)=><path key={j} d={q.d} fill="none" stroke={q.color} strokeWidth={q.strokeWidth} strokeLinecap={m.type==='highlight'?'butt':'round'} strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1-p} opacity={q.opacity} transform={`translate(${q.offsetX??0} ${q.offsetY??0})`} style={{mixBlendMode:q.blend}}/>)}</g>;
   })}
  </svg>
 </OpaquePaper>;
}
