import React from 'react';
import {AbsoluteFill,useCurrentFrame,useVideoConfig} from 'remotion';
import {CourseWorld,OpaquePaper} from './stage';
import {cameraAt} from './camera';
import {defaults} from './defaults';
export default function LayerAndCameraExample({item}:any){
 const frame=useCurrentFrame(),{fps,height}=useVideoConfig(),t=frame/fps,p={...defaults,...(item.props||{})},cam=cameraAt(t,JSON.parse(p.cameraJSON),p.readingPushStrength),u=height/1080;
 return <AbsoluteFill style={{fontFamily:p.font,overflow:'hidden'}}><CourseWorld camera={cam} values={p} id="remotion-example"><OpaquePaper width={1420} height={860}><div style={{padding:48,display:'flex',flexDirection:'column',gap:22}}><div style={{fontSize:50,fontWeight:700}}>同一空间，整体与细节</div><div style={{fontSize:27,color:'#85718F'}}>自制工艺示意 · 不是真实证据页</div></div></OpaquePaper>{[-350,350].map((x,i)=><OpaquePaper key={x} x={x} y={-20} z={40} width={640} height={500} tone={i===0&&t>8.3?.65:1}><div style={{padding:42,display:'flex',flexDirection:'column',gap:28}}><div style={{fontSize:29,color:'#85718F'}}>{i===0?'整体中的一个对象':'贴近当前重点'}</div><div style={{fontSize:65,fontWeight:700,color:p.accentColor,lineHeight:1.25}}>{i===0?'实心纸面':'文字可以很大'}</div><div style={{fontSize:38,lineHeight:1.4}}>{i===0?'退为配角时，背景仍在纸面后。':'每个特写保留完整的主要阅读单位。'}</div></div></OpaquePaper>)}</CourseWorld><div style={{position:'absolute',zIndex:30,left:140*u,top:65*u,fontSize:24*u,color:p.secondaryColor,opacity:cam.s<1?1:0}}>HTML 与 Remotion 共用背景和镜头参数</div></AbsoluteFill>;
}
