# Narração via ElevenLabs (com timestamps por caractere -> sincronia exata)
# uso: ELEVEN_KEY=... python3 narr_eleven.py <voice_id>
import os,sys,json,base64,io,urllib.request,numpy as np,soundfile as sf,subprocess
KEY=os.environ['ELEVEN_KEY'];VID=sys.argv[1]
src=open('narr.py').read();S=eval('['+src.split('S=[',1)[1].split('\n]')[0]+'\n]');GAP=eval(src.split('GAP=')[1].split('\n')[0])
SR=44100;t=.5;out=[];buf=[]
for sid,spk,cap in S:
    req=urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VID}/with-timestamps?output_format=mp3_44100_128',
        data=json.dumps({"text":cap.replace('"',''),"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.25,"use_speaker_boost":True}}).encode(),
        headers={'xi-api-key':KEY,'Content-Type':'application/json'})
    r=json.load(urllib.request.urlopen(req,timeout=120))
    mp3=base64.b64decode(r['audio_base64']);wav=subprocess.run(['ffmpeg','-loglevel','error','-i','-','-f','wav','-ac','1','-ar',str(SR),'-'],input=mp3,capture_output=True).stdout
    a,_=sf.read(io.BytesIO(wav));al=r['alignment'];chars=al['characters'];st=al['character_start_times_seconds'];en=al['character_end_times_seconds']
    # palavras com tempos reais
    words=[];cur='';c0=None
    for ch,s0,e0 in zip(chars,st,en):
        if ch.isspace():
            if cur:words.append(dict(w=cur,t0=round(t+c0,3),t1=round(t+pe,3)));cur=''
        else:
            if not cur:c0=s0
            cur+=ch;pe=e0
    if cur:words.append(dict(w=cur,t0=round(t+c0,3),t1=round(t+pe,3)))
    d=len(a)/SR;out.append(dict(id=sid,start=round(t,3),voice=round(d,3),caption=cap,words=words));buf.append((t,a));t+=d+GAP.get(sid,0.12)
    print(sid,round(d,2))
total=t+.8
for i,o in enumerate(out):o['end']=round(out[i+1]['start'] if i+1<len(out) else total,3)
B=np.zeros(int(total*SR)+SR)
for s0,a in buf:i=int(s0*SR);B[i:i+len(a)]+=a
sf.write('build/voice.wav',B,SR);json.dump(dict(total=round(total,3),scenes=out),open('build/timeline.json','w'),ensure_ascii=False,indent=1)
open('build/timeline.js','w').write('const TIMELINE='+open('build/timeline.json').read()+';')
