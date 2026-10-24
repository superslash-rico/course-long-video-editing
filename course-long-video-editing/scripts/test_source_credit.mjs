import assert from 'node:assert/strict';
import {sourceCreditStyle,sourceCreditDefaults} from '../assets/components/course-stage/source-credit-layout.js';
const checks=[];
for(const [width,height] of [[1920,1080],[3840,2160],[1280,720],[1080,1920]]){
 const s=sourceCreditStyle(width,height),u=height/1080;
 assert.equal(s.left,24*u);assert.equal(s.bottom,18*u);assert.equal(s.fontSize,14*u);
 assert(s.left+s.maxWidth<=width-24*u+.001);assert(s.bottom>0&&s.bottom<height*.025);
 assert(!('top' in s)&&!('transform' in s));checks.push({viewport:[width,height],ok:true});
}
for(const [w,h] of [[0,1080],[1920,0],[-1,1080],[NaN,1080],[1920,Infinity]])assert.throws(()=>sourceCreditStyle(w,h));
assert(Object.isFrozen(sourceCreditDefaults));
console.log(JSON.stringify({ok:true,viewports:checks,invalidDimensionsRejected:5,scope:'Pure screen-space layout bounds and scaling. Actual native text, long-note wrapping and occlusion require visual review.'},null,2));
