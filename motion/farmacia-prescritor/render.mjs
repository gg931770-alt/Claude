import { createRequire } from 'module';const require=createRequire(import.meta.url);const { chromium }=require('playwright');
import { spawn } from 'child_process';
import fs from 'fs';
const mode=process.argv[2]||'stills';
const b=await chromium.launch({args:['--allow-file-access-from-files']});
const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('console',m=>console.log('PAGE:',m.text()));p.on('pageerror',e=>console.log('ERR:',e.message));
await p.goto('file:///tmp/claude-0/motion/build/'+(process.env.PAGE||'index.html')+'');
await p.evaluate(()=>window.READY);
const total=await p.evaluate(()=>TIMELINE.total);
fs.writeFileSync('/tmp/claude-0/motion/build/cues.json',JSON.stringify(await p.evaluate(()=>window.AUDIO_CUES)));
if(mode==='stills'){
  const ts=process.argv.slice(3).map(Number);
  for(const t of ts){await p.evaluate(([t])=>renderAt(t,Math.round(t*30)),[t]);
    const d=await p.evaluate(()=>document.getElementById('c').toDataURL('image/jpeg',.8));
    fs.writeFileSync(`/tmp/claude-0/motion/stills/t${t}.jpg`,Buffer.from(d.split(',')[1],'base64'));}
}else{
  const fps=30,N=Math.ceil(total*fps);
  const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','/tmp/claude-0/motion/build/'+(process.env.OUTV||'video.mp4')],{stdio:['pipe','ignore','inherit']});
  for(let f=0;f<N;f++){const d=await p.evaluate(([f,fps])=>{renderAt(f/fps,f);return document.getElementById('c').toDataURL('image/jpeg',.93);},[f,fps]);
    if(!ff.stdin.write(Buffer.from(d.split(',')[1],'base64')))await new Promise(r=>ff.stdin.once('drain',r));
    if(f%150===0)console.log('frame',f,'/',N);}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));
}
await b.close();
