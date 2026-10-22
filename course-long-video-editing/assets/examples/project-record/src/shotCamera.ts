const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const smooth=(n:number)=>{const t=clamp(n);return t*t*(3-2*t);};
const fast=(n:number)=>{const t=clamp(n);return t*t*t*(t*(t*6-15)+10);};
export function shotCamera(f:number,keys:number[][],screenOffsets=false){
 const same=(a:number[],b:number[])=>[1,2,3,4,5].every(i=>Math.abs((a[i]??0)-(b[i]??0))<1e-7);
 const shots:number[][]=[];for(const row of keys){if(!shots.length||!same(row,shots[shots.length-1]))shots.push(row);}
 const end=keys[keys.length-1][0];
 const pose=(a:number[],push=0)=>{
  const q=1+(a[3]>=.9?.035:.018)*smooth(push);
  return {x:a[1]*(screenOffsets?q:1),y:a[2]*(screenOffsets?q:1),s:a[3]*q,rx:a[4]??0,ry:a[5]??0};
 };
 if(f<=shots[0][0])return pose(shots[0]);
 for(let i=0;i<shots.length-1;i++){
  const a=shots[i],b=shots[i+1];if(f>b[0])continue;
  const duration=Math.max(1,Math.min(b[6]??18,b[0]-a[0]));const depart=b[0]-duration;
  if(f<=depart)return pose(a,(f-a[0])/Math.max(1,depart-a[0]));
  const from=pose(a,depart>a[0]?1:0),to=pose(b),u=fast((f-depart)/duration),mix=(x:number,y:number)=>x+(y-x)*u;
  return {x:mix(from.x,to.x),y:mix(from.y,to.y),s:Math.exp(mix(Math.log(from.s),Math.log(to.s))),rx:mix(from.rx,to.rx),ry:mix(from.ry,to.ry)};
 }
 const last=shots[shots.length-1];return pose(last,(f-last[0])/Math.max(1,end-last[0]));
}
