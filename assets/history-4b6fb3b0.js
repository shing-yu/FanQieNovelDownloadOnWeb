import{_ as g,r as n,k as m,o as l,c as i,a as s,F as _,l as w,w as b,f as k,u as h,t as p,h as d,n as S,g as x,p as F,i as I,j as A}from"./bootstrap.min-c4c061eb.js";const D=a=>(F("data-v-395192f9"),a=a(),I(),a),$=D(()=>s("div",{class:"title"},[s("h1",{class:"display-4"},"下载任务")],-1)),B={class:"centered-div"},C={class:"progress"},L=["onClick"],N={class:"alert alert-success"},V={__name:"App",setup(a){const r=n([]);let c=n(!1),u=n("");const y=async(e,o)=>{c.value=!1;try{const t=await d.get(`http://127.0.0.1:8000/api/down/del/${e}/`);c.value=!0,location.reload()}catch(t){console.error("Failed to fetch history data:",t)}},f=async()=>{try{const e=await d.get("http://127.0.0.1:8000/api/history/");r.value=e.data,v()}catch(e){console.error("Failed to fetch history data:",e)}},v=()=>{setInterval(async()=>{for(const e of r.value.history)if(e.percent!==100)try{const o=await d.get(`http://127.0.0.1:8000/api/history/${e.obid}/`);e.percent=o.data.percent}catch(o){console.error("Failed to fetch progress:",o)}},800)};return m(()=>{f()}),(e,o)=>(l(),i(_,null,[$,s("div",B,[(l(!0),i(_,null,w(r.value.history,t=>(l(),i("div",{key:t.obid,class:"history-item"},[s("h2",null,p(t.file_name),1),s("div",C,[s("div",{class:"progress-bar",style:S({width:`${t.percent}%`})},null,4)]),x(p(t.percent)+"% ",1),s("button",{class:"btn btn-danger mt-3",onClick:z=>y(t.obid,t.file_name)},"删除",8,L)]))),128)),b(s("div",N,[s("strong",null,p(h(u))+" 删除成功!",1)],512),[[k,h(c)]])])],64))}},j=g(V,[["__scopeId","data-v-395192f9"]]);A(j).mount("#app");