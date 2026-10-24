import React from 'react';
import {AbsoluteFill,useVideoConfig} from 'remotion';
import {sourceCreditStyle} from './source-credit-layout';
// Mount as a top-level sibling of CourseWorld / CameraStage, never inside them.
export function SourceCredit({text,fontFamily='MiSans',opacity=1}:any){
 const {width,height}=useVideoConfig();
 if(!String(text??'').trim())return null;
 return <AbsoluteFill style={{zIndex:100,pointerEvents:'none',opacity}}><div data-source-credit="screen-bottom-left" style={{...sourceCreditStyle(width,height),fontFamily} as any}>{text}</div></AbsoluteFill>;
}
