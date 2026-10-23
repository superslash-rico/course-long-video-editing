import {createBackground} from '../../components/course-stage/background.js';
import {backgroundDefaults} from '../../components/course-stage/background.js';
export default function mount({root,props}){let p={...backgroundDefaults,label:'名牌与金句组件示范',...(props||{})};const bg=createBackground(root.querySelector('.gallery'),{id:'gallery'});function bind(){root.querySelector('.gallery-label').textContent=p.label;}bind();return{update({props}){p={...backgroundDefaults,label:'名牌与金句组件示范',...(props||{})};bind();},render(){bg.render(p,{s:.77,fx:0,fy:0});},dispose(){bg.dispose();}};}
