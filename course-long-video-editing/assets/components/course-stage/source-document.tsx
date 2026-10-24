import React from 'react';
import {Img} from 'remotion';
import {OpaquePaper} from './stage';
import {phase} from './camera';

// A real image and all its marks share the SAME source-pixel coordinate plane.
// src is supplied by the receiving project's actual media binding, never a demo ID.
export function SourceDocument({src,sourceWidth,sourceHeight,width=1280,x=0,y=0,z=96,timeSeconds=0,marks=[],tone=1,reveal=1}:any){
 if(!src||![sourceWidth,sourceHeight,width].every(v=>Number.isFinite(v)&&v>0))throw new Error('Bind a verified source image and its actual pixel dimensions');
 const unit=width/sourceWidth,height=sourceHeight*unit;
 return <OpaquePaper x={x} y={y} z={z} width={width} height={height} tone={tone} reveal={reveal}>
  <Img src={src} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/>
  <svg viewBox={`0 0 ${sourceWidth} ${sourceHeight}`} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
   {marks.map((m,i)=>{
    const [a,b,w,h]=m.rect??[],p=phase(timeSeconds,m.at??0,(m.at??0)+(m.draw??.52));
    if(![a,b,w,h].every(Number.isFinite)||Math.min(a,b)<0||Math.min(w,h)<=0||a+w>sourceWidth||b+h>sourceHeight)throw new Error('Annotation must remain within its source image');
    if(!p)return null;
    const common={fill:'none',stroke:m.color??'#DA332C',strokeWidth:(m.stroke??2.5)/unit,strokeLinecap:'round' as const,strokeLinejoin:'round' as const,pathLength:1,strokeDasharray:1,strokeDashoffset:1-p};
    if(m.type==='highlight')return <rect key={i} x={a} y={b} width={w*p} height={h} rx={2/unit} fill={m.color??'#FFE259'} opacity={.36} style={{mixBlendMode:'multiply'}}/>;
    if(m.type==='underline')return <path key={i} {...common} d={`M${a} ${b+h} Q${a+w*.5} ${b+h+1/unit} ${a+w} ${b+h}`}/>;
    if(m.type==='circle')return <path key={i} {...common} d={`M${a+w*.5} ${b} C${a+w*1.1} ${b-h*.08} ${a+w*1.1} ${b+h*1.08} ${a+w*.5} ${b+h} C${a-w*.1} ${b+h*1.08} ${a-w*.1} ${b-h*.08} ${a+w*.5} ${b}`} />;
    if(m.type!=='frame')throw new Error('Unknown source annotation type');
    return <rect key={i} {...common} x={a} y={b} width={w} height={h} rx={4/unit}/>;
   })}
  </svg>
 </OpaquePaper>;
}
