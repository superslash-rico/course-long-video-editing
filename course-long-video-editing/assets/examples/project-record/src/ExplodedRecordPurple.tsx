import {DotBackdrop} from './DotBackdrop';
import {shotCamera} from './shotCamera';
import {cameraPlan} from './cameraPlan';
// Rico lesson 4 · brand-purple revision, native spatial choreography retained.
// Adapted from video-shotcraft 43bd349a136651865ecfa6ea1cf012f6e957d304 (Apache-2.0).
// Stage, readable callout columns and concluding camera reserve the lower-right
// 284 px live presenter circle. Original five-surface explode/reassembly retained.
import React from 'react';
import { AbsoluteFill, useCurrentFrame,useVideoConfig } from 'remotion';
import { LOOKS, Sheen, Stage, TextReveal, alpha, springAt, type } from './_fixtures/Look';
import { EASE, FONT, mix, ramp } from './_fixtures/Polish';


const EXPLODED_VIEW_DURATION = 170;

const L = {...LOOKS.porcelain, accent:'#9B22AF', line:'#E9DEEE', shadow:'#26132E', ink:'#231529', bg:['#FCFAFD','#F4EEF7','#EBE0F0']};
const W = 1600;
const H = 1000;
const R = 26; // 页面圆角
const PERSP = 2400;

const EXPLODE = 24;
const STAGGER = 5;
const ASSEMBLE = 108;
const BACK = 3; // 合体错峰
const BACK_DUR = 14;

type Layer = {
  key: string; x: number; y: number; w: number; h: number; z: number; r: number; side: 'L' | 'R';
  label: { n: string; t: string; d: string };
};

// 层（页面坐标 + 炸开高度）；order = 数组下标（底 → 顶）
const LAYERS: Layer[] = [
  { key: 'side', x: 0, y: 0, w: 288, h: H, z: 150, r: R, side: 'L', label: { n: '01', t: 'Navigation', d: 'Every shot, one click away' } },
  { key: 'chart', x: 320, y: 410, w: 860, h: 558, z: 270, r: 22, side: 'L', label: { n: '02', t: 'Insights', d: 'Renders, timing and pace' } },
  { key: 'ai', x: 1204, y: 410, w: 364, h: 558, z: 400, r: 22, side: 'R', label: { n: '03', t: 'Assistant', d: 'Drafts shots you approve' } },
  { key: 'kpi', x: 320, y: 130, w: W - 352, h: 250, z: 520, r: 22, side: 'R', label: { n: '04', t: 'Live metrics', d: 'Updated every second' } },
  { key: 'top', x: 288, y: 0, w: W - 288, h: 100, z: 640, r: 0, side: 'R', label: { n: '05', t: 'Command bar', d: 'Add a shot in one line' } },
];
const N = LAYERS.length;

// Content is data-driven; the five original independently lifted surfaces remain.
const ink=(c:string,s:number,w:number,extra:any={})=>({...type(s,w),color:c,fontFamily:'var(--record-font)',...extra});
const Panel: React.FC<{ly:Layer;data:any}> = ({ly,data}) => {
 const narrow=ly.key==='side'||ly.key==='ai',strip=ly.key==='top',checks=ly.key==='kpi';
 const lines=String(data.body||'').split('\n');
 return <div style={{position:'absolute',inset:0,boxSizing:'border-box',padding:strip?'19px 32px':narrow?'33px 27px':'34px 38px',background:ly.key==='ai'?'linear-gradient(150deg,#fff,#F2E5F6)':'#fff',borderRadius:ly.r,boxShadow:'inset 0 0 0 2px '+L.line,color:L.ink,display:'flex',flexDirection:strip?'row':'column',alignItems:strip?'center':undefined,gap:strip?30:24}}>
  <div style={{...ink(L.accent,strip?39:narrow?42:48,740),lineHeight:1.18,flexShrink:0}}>{data.t}</div>
  <div style={{display:'flex',flexDirection:checks?'row':'column',gap:checks?32:22,flex:1}}>{lines.map((s:string,i:number)=><div key={i} style={{...ink(L.ink,strip?28:narrow?35:checks?40:42,490),lineHeight:1.45,padding:checks?'16px 24px':0,borderRadius:checks?15:0,background:checks?'#F7F1F9':undefined,flex:checks?1:undefined}}>{s}</div>)}</div>
 </div>;
};
const mapClock=(frame:number,clock:number[][])=>{for(let i=0;i<clock.length-1;i++){let a=clock[i],b=clock[i+1];if(frame<=b[0])return mix(a[1],b[1],Math.max(0,Math.min(1,(frame-a[0])/(b[0]-a[0]))));}return clock[clock.length-1][1];};


// ───────────── 机位与投影 ─────────────
type Cam = { rx: number; rz: number; s: number; cx: number; cy: number };
const camAt = (f: number): Cam => {
  const orbit = ramp(f, 30, 74, EASE.smooth);
  const push = ramp(f, 0, 170, EASE.smooth);
  const outro = ramp(f, 132, 30, EASE.smooth); // 合体后机位右移，给左上角标题让位
  // 机位跟着层堆的高度走：炸开时整组下移，让最高的层也留在画里；合体后回升
  const tall = ramp(f, 22, 40, EASE.smooth) * (1 - ramp(f, 106, 30, EASE.smooth));
  return {
    rx: mix(54, 50, orbit),
    rz: mix(-34, -32, ramp(f, 0, 30, EASE.out)) + 10 * orbit,
    s: mix(0.50, 0.42, tall) * mix(1, 1.04, push), // 炸开时拉远给层堆留画面，合体后推回
    cx: mix(-60, 90, outro),
    cy: mix(5, 105, tall) + 5 * outro,
  };
};
// 页面点 (px,py,pz) → 屏幕坐标：与 CSS transform `translate(cx,cy) scale(s) rotateX(rx) rotateZ(rz)` +
// perspective(PERSP) 同一套矩阵（origin = 页面中心 = 屏幕中心）
const project = (c: Cam, px: number, py: number, pz: number) => {
  const X = px - W / 2, Y = py - H / 2;
  const a = (c.rz * Math.PI) / 180, b = (c.rx * Math.PI) / 180;
  const x1 = X * Math.cos(a) - Y * Math.sin(a);
  const y1 = X * Math.sin(a) + Y * Math.cos(a);
  const y2 = y1 * Math.cos(b) - pz * Math.sin(b);
  const z2 = y1 * Math.sin(b) + pz * Math.cos(b);
  const x4 = x1 * c.s + c.cx, y4 = y2 * c.s + c.cy;
  const k = PERSP / (PERSP - z2);
  return { x: 960 + x4 * k, y: 540 + y4 * k };
};

// 每层炸开进度：弹簧上升 × 逆序 ease-in 合体
const layerP = (f: number, i: number) => {
  const up = springAt(f, EXPLODE + i * STAGGER, { damping: 15, stiffness: 120 });
  const down = ramp(f, ASSEMBLE + (N - 1 - i) * BACK, BACK_DUR, EASE.exit);
  return up * (1 - down);
};
const CLOSE = ASSEMBLE + (N - 1) * BACK + BACK_DUR; // 合体落座帧 = 134

// Portable derivative: unused connector callouts removed; labels live on each surface.
const framingCam=(real:number,f:number):Cam=>{
 const keys=cameraPlan.map(a=>{
  if((a[7]??-1)<0)return a;
  const ly=LAYERS[a[7]],pz=ly.z*layerP(f,a[7])+2;
  const x=a[1]-W/2,y=a[2]-H/2,b=a[4]*Math.PI/180,c=a[5]*Math.PI/180;
  const u=x*Math.cos(c)-y*Math.sin(c),v=x*Math.sin(c)+y*Math.cos(c);
  const yy=v*Math.cos(b)-pz*Math.sin(b),zz=v*Math.sin(b)+pz*Math.cos(b),k=PERSP/(PERSP-zz);
  return [a[0],-u*a[3],(420-540)/k-yy*a[3],a[3],a[4],a[5],a[6]??18];
 });
 const lens=shotCamera(real,keys,true);return {cx:lens.x,cy:lens.y,s:lens.s,rx:lens.rx,rz:lens.ry};
};

export default function ExplodedRecord({item}:any) {
  const frame=useCurrentFrame();const {fps}=useVideoConfig();
 // Preserve the authored 30fps cue clock while deriving playback from seconds.
 const real=frame*(30/fps),p=item.props;
  const labels=JSON.parse(p.labelsJSON),clock=JSON.parse(p.clockJSON),conclusions=JSON.parse(p.conclusionJSON);
  const f=mapClock(real,clock);
  const cam = framingCam(real,f);
  const chrome=1-ramp(real,100,14,EASE.smooth)*(1-ramp(real,402,16,EASE.smooth));
  // 预备：层整体下压；落锤：整组下沉回弹
  const crouch = -6 * (ramp(f, 18, 6, EASE.out) * (1 - ramp(f, EXPLODE, 6, EASE.out)));
  const since = f - CLOSE;
  const thud = since >= 0 ? 8 * Math.exp(-since / 3) * Math.cos(since * 0.9) : 0;
  const spread = ramp(f, EXPLODE, 30, EASE.out) * (1 - ramp(f, ASSEMBLE, CLOSE - ASSEMBLE, EASE.exit));
  const sheen = ramp(f, CLOSE + 4, 24, EASE.swift);

  return (
    <AbsoluteFill style={{ overflow: 'hidden', fontFamily:p.fontFamily, '--record-font':p.fontFamily, '--record-accent':p.accentColor, opacity:ramp(real,0,8,EASE.out)*(1-ramp(real,p.seconds*30-8,8,EASE.exit)) } as any}>
      <DotBackdrop p={p} cam={cam}/>

      <AbsoluteFill style={{ perspective: PERSP }}>
        <div style={{
          position: 'absolute', left: 960 - W / 2, top: 540 - H / 2, width: W, height: H, transformStyle: 'preserve-3d',
          transform: `translate(${cam.cx}px, ${cam.cy + thud}px) scale(${cam.s}) rotateX(${cam.rx}deg) rotateZ(${cam.rz}deg)`,
        }}>
          {/* 台面接触影：整页落在台面上的大软影（炸开时变淡，落锤时一紧） */}
          <div style={{
            position: 'absolute', left: -20, top: 10, width: W + 40, height: H + 40, borderRadius: R + 20,
            background: alpha(L.shadow, 0.28 - 0.08 * spread + 0.06 * Math.max(0, thud / 8)),
            filter: `blur(${40 - 10 * Math.max(0, thud / 8)}px)`, transform: 'translateZ(-30px) translate(30px, 40px)',
          }} />
          {/* 底板厚度 */}
          <div style={{ position: 'absolute', inset: 0, borderRadius: R, background: '#D8C5E2', transform: 'translateZ(-14px)' }} />
          {/* 底板：页面背景 + 构件插槽虚线 */}
          <div style={{ position: 'absolute', inset: 0, borderRadius: R, overflow: 'hidden', background: `linear-gradient(160deg, #F7F1F9 0%, ${L.bg[2]} 100%)`, boxShadow: `inset 0 0 0 2px ${L.line}` }}>
            {LAYERS.map((ly) => (
              <div key={ly.key} style={{
                position: 'absolute', left: ly.x + 10, top: ly.y + 10, width: ly.w - 20, height: ly.h - 20, borderRadius: Math.max(10, ly.r - 6),
                border: `3px dashed ${alpha(L.accent, 0.28)}`, background: alpha(L.accent, 0.03), boxSizing: 'border-box', opacity: Math.min(1, spread * 2),
              }} />
            ))}
            {/* 扫光：合体后一次（裁进底板圆角） */}
            <Sheen progress={sheen} color="#ffffff" strength={0.6} width={0.18} />
          </div>
          {/* 层投到底板上的影：随高度下移、变虚、变淡（主光左上 → 影向右下） */}
          {LAYERS.map((ly, i) => {
            const p = Math.max(0, layerP(f, i));
            if (p < 0.01) return null;
            const h = ly.z * p;
            return (
              <div key={`sh-${ly.key}`} style={{
                position: 'absolute', left: ly.x + h * 0.18, top: ly.y + h * 0.26, width: ly.w, height: ly.h, borderRadius: ly.r,
                background: alpha(L.shadow, 0.3), filter: `blur(${(10 + h * 0.09).toFixed(1)}px)`, opacity: Math.min(1, p * 1.5) * (0.8 - h / 1400),
                transform: 'translateZ(1px)',
              }} />
            );
          })}
          {/* 可动层：沿法线升起；背后一片厚度边（钴蓝灰） */}
          {LAYERS.map((ly, i) => {
            const p = layerP(f, i);
            const z = ly.z * p + 2;
            const data=labels.find((d:any)=>d.key===ly.key);
            const box: React.CSSProperties = { position: 'absolute', left: ly.x, top: ly.y, width: ly.w, height: ly.h, borderRadius: ly.r };
            const lifted = Math.min(1, Math.max(0, p) * 4);
            return (
              <React.Fragment key={ly.key}>
                {lifted > 0.02 && <div style={{ ...box, background: '#C9ADD6', transform: `translateZ(${Math.max(2.5, z - 8 + crouch).toFixed(2)}px)` }} />}
                <div style={{
                  ...box, overflow: 'hidden', transform: `translateZ(${(z + crouch).toFixed(2)}px)`,
                  boxShadow: lifted > 0.02 ? `0 0 0 2px ${alpha('#ffffff', 0.9 * lifted)}` : undefined,
                }}>
                  <Panel ly={ly} data={data}/>
                </div>
              </React.Fragment>
            );
          })}
        </div>
      </AbsoluteFill>

      {/* 标注：锚点（层右缘中点的 3D 投影）→ 折线引线 → 编号 + 标题 + 说明 */}
      {/* Per-panel titles carry the meaning; connector callouts are not used in macro shots. */}

      <div style={{position:'absolute',left:94,top:63,width:1490,color:p.textColor,opacity:chrome}}>
        <div style={{fontSize:25,fontWeight:600,color:p.accentColor,letterSpacing:2,marginBottom:18}}>项目记录</div>
        <div style={{fontSize:65,fontWeight:740,lineHeight:1.15,color:p.headingColor}}>{real<438?p.title:p.closingTitle}</div>
        <div style={{fontSize:31,lineHeight:1.4,color:'#D9CCD9',marginTop:18,opacity:1-ramp(real,431,14,EASE.out)}}>{p.subtitle}</div>
      </div>
      <div style={{position:'absolute',left:98,top:337,width:520,display:'flex',flexDirection:'column',gap:33}}>
       {conclusions.map((v:any,i:number)=>{let a=ramp(real,v.at,12,EASE.out);return <div key={i} style={{opacity:a,transform:'translateY('+((1-a)*23)+'px)',display:'flex',alignItems:'baseline',gap:24}}><div style={{fontSize:70,fontWeight:730,color:i===2?p.headingColor:p.textColor,lineHeight:1.15}}>{v.text}</div><div style={{fontSize:30,color:'#C8B6CE'}}>{v.detail}</div></div>;})}
      </div>
    </AbsoluteFill>
  );
};

