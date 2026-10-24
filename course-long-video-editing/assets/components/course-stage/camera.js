// Seconds-based authored camera. No ticker, wall clock, or previous-frame state.
export const clamp=v=>Math.max(0,Math.min(1,v));
export const smooth=v=>{const x=clamp(v);return x*x*x*(x*(x*6-15)+10);};
export const phase=(t,a,b)=>smooth((t-a)/Math.max(.000001,b-a));
export const mix=(a,b,k)=>a+(b-a)*k;
export function validateShots(shots,duration=Infinity){
 if(!(duration>0))throw new Error('Provide a positive scene duration');
 if(!Array.isArray(shots)||!shots.length)throw new Error('Provide a nonempty camera plan in seconds');
 shots.forEach((q,i)=>{
  if(!Number.isFinite(q.at)||!Number.isFinite(q.until)||q.at<0||q.until<q.at||q.until>duration)throw new Error('Invalid shot time');
  if(i&&q.at<shots[i-1].until)throw new Error('Camera reading holds overlap');
  if(!q.p||!Number.isFinite(q.p.s)||q.p.s<=0||!Number.isFinite(q.p.fx)||!Number.isFinite(q.p.fy))throw new Error('Invalid camera pose');
  if(['rx','ry','rz','fz'].some(k=>q.p[k]!==undefined&&!Number.isFinite(q.p[k])))throw new Error('Invalid camera angle');
  if(i&&q.at===shots[i-1].until&&q.cut!==true&&['fx','fy','fz','s','rx','ry','rz'].some(k=>(q.p[k]??0)!==(shots[i-1].p[k]??0)))throw new Error('A zero-time pose change must be an intentional cut');
  if(q.orbit!==undefined&&(!Number.isFinite(q.orbit)||Math.abs(q.orbit)>15))throw new Error('Invalid reading orbit');
  if(q.push!==undefined&&(!Number.isFinite(q.push)||q.push<0||q.push>.3))throw new Error('Invalid reading push');
 });
 return shots;
}
export function cameraAt(time,shots,strength=1){
 if(!Number.isFinite(time)||!Number.isFinite(strength)||strength<0||strength>2)throw new Error('Invalid time or reading strength');
 const hold=(q,t)=>({...q.p,s:q.p.s*(1+(q.push??(q.p.s>1?.08:.05))*strength*phase(t,q.at,q.until)),ry:(q.p.ry??0)+(q.orbit??0)*strength*phase(t,q.at,q.until)});
 if(time<=shots[0].at)return hold(shots[0],shots[0].at);
 for(let i=0;i<shots.length;i++){
  const a=shots[i],b=shots[i+1];
  if(b&&b.cut===true&&time>=b.at&&b.at===a.until)continue;
  if(!b||time<=a.until)return hold(a,time);
  if(time<b.at){const from=hold(a,a.until),k=phase(time,a.until,b.at),out={};
   for(const key of ['fx','fy','fz','rx','ry','rz'])out[key]=mix(from[key]??0,b.p[key]??0,k);
   out.s=Math.exp(mix(Math.log(from.s),Math.log(b.p.s),k));return out;
  }
 }
 return hold(shots[shots.length-1],time);
}
export const exampleShots=[
 {at:0,until:3.0,p:{fx:0,fy:0,s:.77,rx:20,rz:-1}},
 {at:3.36,until:8.15,p:{fx:-350,fy:70,s:1.65,rx:9,rz:0}},
 {at:8.51,until:14.9,p:{fx:350,fy:70,s:1.65,rx:9,rz:0}},
 {at:15.26,until:18.2,p:{fx:0,fy:0,s:.77,rx:20,rz:-1}},
 {at:18.56,until:22.8,p:{fx:-155,fy:80,s:1.6,rx:9,rz:0}},
 {at:23.16,until:24,p:{fx:0,fy:0,s:.77,rx:20,rz:-1}}
];

// Shared by HTML and Remotion so foreground binding uses one actual transform.
export function cameraTransform(p){return `scale3d(${p.s},${p.s},${p.s}) rotateX(${p.rx??0}deg) rotateY(${p.ry??0}deg) rotateZ(${p.rz??0}deg) translate3d(${-p.fx}px,${-p.fy}px,${-(p.fz??0)}px)`;}
