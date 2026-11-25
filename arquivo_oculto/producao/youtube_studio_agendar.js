// Agendamento de Shorts no YouTube Studio (canal O Arquivista Oculto), testado em 17–18/11/2026.
// Como usar: abrir https://studio.youtube.com/channel/UCiDZLhTLU-T7vJdpCrctvuw/videos/short numa aba nova,
// colar este código no javascript_tool (Claude in Chrome) com FILA preenchida (3 ou 4 itens por vez,
// tirados de youtube_fila_pendente.json) e depois ler document.documentElement.dataset.ytlog.
// O vídeo precisa estar hospedado com CORS liberado (Higgsfield: media_upload → PUT → media_confirm).
//
// Segurança embutida: nunca clica em "Avançar" na etapa de visibilidade (o padrão do canal é Público);
// escolhe o dia no calendário e a hora na lista (texto digitado pode não gravar); só clica em "Programar"
// depois de conferir data e hora; lê a janela "Vídeo programado" e a fecha pelo #close-button.
// Pare antes de renderizar algo pesado na máquina: com pouca RAM o Chrome congela e a aba cai.
const FILA = [/* {t, url, titulo, desc, data:'20 de nov. de 2026', hora:'10:30', dia:20} */];
const S=ms=>new Promise(r=>setTimeout(r,ms));
const LOG=m=>{document.documentElement.dataset.ytlog=(document.documentElement.dataset.ytlog||'')+' | '+m;};
const W=async(f,t=150000)=>{const s=Date.now();while(Date.now()-s<t){try{const v=f();if(v)return v;}catch(e){if(/LIMITE/.test(e.message))throw e;}await S(400);}throw new Error('timeout '+f.toString().slice(6,50));};
const vis=e=>!!e&&e.offsetParent!==null;
const T=async(el,x)=>{el.focus();await S(150);document.execCommand('selectAll',false,null);document.execCommand('insertText',false,x);await S(200);};
const fecharConf=async()=>{for(let k=0;k<3;k++){const dl=[...document.querySelectorAll('ytcp-dialog, tp-yt-paper-dialog')].find(e=>vis(e)&&/Processando v|deo programado/i.test(e.innerText||''));if(!dl)break;const b=dl.querySelector('#close-button')||dl.querySelector('#close-icon-button');if(b)b.click();await S(1500);}};
const faseA=async(o)=>{await fecharConf();await S(1500);document.querySelector('button[aria-label="Criar"]').click();
 (await W(()=>[...document.querySelectorAll('tp-yt-paper-item,[role=menuitem]')].find(e=>vis(e)&&/Enviar v/i.test(e.innerText)),30000)).click();
 const inp=await W(()=>document.querySelector('ytcp-uploads-file-picker input[type=file]'),30000);
 const b=await fetch(o.url).then(r=>{if(!r.ok)throw new Error('fetch '+r.status);return r.blob()});
 const dt=new DataTransfer();dt.items.add(new File([b],o.t+'.mp4',{type:'video/mp4'}));inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));
 const d=await W(()=>{const x=document.querySelector('ytcp-uploads-dialog');if(x&&/limite di|daily upload limit|limite de envio/i.test(x.innerText))throw new Error('LIMITE');return x&&vis(x.querySelector('#title-textarea #textbox'))?x:null},60000);
 await S(3000);await T(d.querySelector('#title-textarea #textbox'),o.titulo);await T(d.querySelector('#description-textarea #textbox'),o.desc);
 d.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').click();
 const tg=d.querySelector('#toggle-button');if(tg)tg.click();await S(1500);
 const sim=[...d.querySelectorAll('tp-yt-paper-radio-button')].find(r=>/ALTER.*YES|YES.*ALTER/i.test(r.getAttribute('name')||''));if(sim)sim.click();
 for(let i=0;i<6;i++){if(vis(d.querySelector('#second-container-expand-button')))break;const nb=d.querySelector('#next-button');if(!vis(nb))throw new Error('next invisivel');nb.click();await S(2500);}
 const ex=d.querySelector('#second-container-expand-button');if(!vis(ex))throw new Error('sem programar');ex.click();await S(1500);return d;};
const faseB=async(o,d)=>{const tr=[...document.querySelectorAll('#datepicker-trigger')].find(vis);
 if(tr.innerText.trim()!==o.data){const dias=()=>[...document.querySelectorAll('ytcp-scrollable-calendar span.calendar-day')].filter(vis);
  const achar=()=>{const ds=dias();const i0=ds.findIndex(s=>s.classList.contains('today'));return i0<0?null:ds.slice(i0).find(s=>s.textContent.trim()===String(o.dia));};
  let alvo=achar();if(!alvo){tr.click();const t0=Date.now();while(!alvo&&Date.now()-t0<45000){await S(800);alvo=achar();}}
  if(!alvo){tr.click();const t0=Date.now();while(!alvo&&Date.now()-t0<30000){await S(800);alvo=achar();}}
  if(!alvo)throw new Error('calendario nao abriu');alvo.click();await S(1500);if(tr.innerText.trim()!==o.data)throw new Error('data nao pegou: '+tr.innerText.trim());}
 const ti=[...document.querySelectorAll('#time-of-day-container input')].find(vis);ti.click();
 let op=null;const t1=Date.now();while(!op&&Date.now()-t1<30000){await S(800);op=[...document.querySelectorAll('tp-yt-paper-item,[role=option]')].find(e=>vis(e)&&e.innerText.trim()===o.hora);}
 if(!op)throw new Error('lista de horas nao abriu');op.scrollIntoView({block:'center'});await S(300);op.click();await S(1000);
 const done=[...document.querySelectorAll('#done-button')].find(vis);
 if(!(tr.innerText.trim()===o.data&&ti.value===o.hora&&/Programar/i.test(done.innerText)))throw new Error('conferencia falhou data='+tr.innerText.trim()+' hora='+ti.value);
 done.click();
 const conf=await W(()=>[...document.querySelectorAll('ytcp-dialog, tp-yt-paper-dialog')].find(e=>vis(e)&&/Processando v|deo programado/i.test(e.innerText||'')),90000);
 const m=(conf.innerText||'').match(/em (\d+ de \S+ de \d{4}) às (\d{2}:\d{2})/);return m?m[1]+' '+m[2]:'confirmado';};
(async()=>{document.documentElement.dataset.ytlog='';for(const o of FILA){try{const d=await faseA(o);const c=await faseB(o,d);LOG('OK '+o.t+' -> '+c);}catch(e){LOG('PAROU '+o.t+': '+e.message);break;}}await fecharConf();LOG('FIM');})();
