// Screen-space source credit; independent of the scene camera.
export const sourceCreditDefaults=Object.freeze({left:24,bottom:18,right:24,fontSize:14,maxWidth:1400});
export function sourceCreditStyle(width,height){
 if(!Number.isFinite(width)||!Number.isFinite(height)||width<=0||height<=0)throw new Error('Use the actual positive viewport');
 const u=height/1080,d=sourceCreditDefaults;
 return {position:'absolute',left:d.left*u,bottom:d.bottom*u,maxWidth:Math.max(1,Math.min(d.maxWidth*u,width-(d.left+d.right)*u)),fontSize:d.fontSize*u,lineHeight:1.3,padding:`${4*u}px ${7*u}px`,boxSizing:'border-box',color:'#D7CFDE',background:'rgba(12,10,20,.58)',borderRadius:2*u,whiteSpace:'normal',overflowWrap:'anywhere',fontWeight:400};
}
