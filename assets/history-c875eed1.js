import{_ as w,r as c,l as k,o as a,c as r,a as o,F as u,h as m,w as F,f as S,u as p,t as _,i as l,n as x,g as D,p as I,j as A,k as $}from"./bootstrap.min-e5701824.js";const B=n=>(I("data-v-fe796a4e"),n=n(),A(),n),C=B(()=>o("div",{class:"title"},[o("h1",{class:"display-4"},"下载任务")],-1)),L={class:"centered-div"},N={class:"progress"},V={class:"progress-div"},j=["href"],z={key:1,class:"btn btn-secondary",disabled:""},E=["onClick"],H={class:"alert alert-success"},M={__name:"App",setup(n){const i=c([]);let d=c(!1),y=c(""),h=c("");document.title="番茄小说下载器 | 下载任务";const f=async(e,s)=>{d.value=!1;try{const t=await l.get(`/api/down/del/${e}/`);d.value=!0,location.reload()}catch(t){console.error("Failed to fetch history data:",t)}},v=async()=>{try{const e=await l.get("/api/history/");i.value=e.data,console.log(e.data),console.log(typeof e.data),g()}catch(e){console.error("Failed to fetch history data:",e)}},g=()=>{setInterval(async()=>{for(const e of i.value.history)if(e.percent!==100)try{const s=await l.get(`/api/history/${e.obid}/`);e.percent=s.data.percent,console.log(e.percent)}catch(s){console.error("Failed to fetch progress:",s)}},800)},b=async()=>{try{const e=await l.get("/api/get_download_url/");console.log(e.data),h.value=e.data.download_url}catch(e){console.error("Failed to fetch history data:",e)}};return k(()=>{v(),b()}),(e,s)=>(a(),r(u,null,[C,o("div",L,[(a(!0),r(u,null,m(i.value.history,t=>(a(),r("div",{key:t.obid,class:"history-item"},[o("h2",null,_(t.file_name),1),o("div",N,[o("div",{class:"progress-bar",style:x({width:`${t.percent}%`})},null,4)]),o("div",V,[D(_(t.percent)+"% ",1),t.percent===100?(a(),r("a",{key:0,href:p(h)+t.file_name,class:"btn btn-primary"}," 下载 ",8,j)):(a(),r("button",z," 下载 ")),o("button",{class:"btn btn-danger mt-3",onClick:T=>f(t.obid,t.file_name)},"删除",8,E)])]))),128)),F(o("div",H,[o("strong",null,_(p(y))+" 删除成功!",1)],512),[[S,p(d)]])])],64))}},P=w(M,[["__scopeId","data-v-fe796a4e"]]);$(P).mount("#app");