import json, numpy as np, soundfile as sf
SR=48000; R=np.random.default_rng(42)
def t(d): return np.arange(int(d*SR))/SR
def env(n,a=.005,r=None,curve=4):
    x=np.ones(n); na=max(1,int(a*SR)); x[:na]=np.linspace(0,1,na)
    tail=np.linspace(1,0,n-na)**curve if r is None else None
    x[na:]=tail; return x
def svf(x,fc,q=.7,mode='bp'):
    # state-variable filter com fc variável (array ou escalar)
    fc=np.broadcast_to(np.asarray(fc,float),x.shape); f=2*np.sin(np.pi*np.clip(fc,20,SR/6)/SR)
    lp=bp=0.;out=np.empty_like(x);d=1/q
    for i in range(len(x)):
        hp=x[i]-lp-d*bp; bp+=f[i]*hp; lp+=f[i]*bp
        out[i]= bp if mode=='bp' else lp if mode=='lp' else hp
    return out
def fftf(x,lo=0,hi=SR/2):
    X=np.fft.rfft(x);fr=np.fft.rfftfreq(len(x),1/SR);X[(fr<lo)|(fr>hi)]=0;return np.fft.irfft(X,len(x))
def norm(x,p=1.): m=np.max(np.abs(x))+1e-9; return x/m*p
def noise(d): return R.standard_normal(int(d*SR))
def sine_sweep(f0,f1,d,shape=2):
    tt=t(d);f=f0+(f1-f0)*(tt/d)**(1/shape) if f1>f0 else f1+(f0-f1)*(1-tt/d)**shape
    return np.sin(2*np.pi*np.cumsum(f)/SR)
def bell(fs,d,decay=6):
    tt=t(d);return sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*decay*(1+i*.5))/(i+1) for i,f in enumerate(fs))
SFX={}
def seqmix(parts,total):
    out=np.zeros(int(total*SR))
    for at,x in parts:
        i=int(at*SR);x=x[:len(out)-i];out[i:i+len(x)]+=x
    return out
def mk(name,fn): SFX[name]=norm(fn(),.9)
d=.55;n=int(d*SR);tt=t(d)
mk('whoosh',lambda: svf(noise(.55),400+3600*np.sin(np.pi*t(.55)/.55)**2,1.2)*np.sin(np.pi*t(.55)/.55)**1.5)
mk('trans',lambda: svf(noise(.4),300+5000*(t(.4)/.4)**1.5,1.5)*np.sin(np.pi*t(.4)/.4)**2)
mk('whoosh_up',lambda: svf(noise(.5),300+6000*(t(.5)/.5)**2,1.4)*(t(.5)/.5)**1.2*np.exp(-np.maximum(0,t(.5)-.42)*40))
mk('whoosh_down',lambda: svf(noise(.45),5000-4500*(t(.45)/.45)**.6,1.4)*np.sin(np.pi*t(.45)/.45)**1.5)
mk('swipe',lambda: svf(noise(.22),1200+6000*(t(.22)/.22),2.5)*np.sin(np.pi*t(.22)/.22))
mk('pop',lambda: sine_sweep(900,260,.12,1.5)*np.exp(-t(.12)*28)+.3*fftf(noise(.12),2000)*np.exp(-t(.12)*90))
mk('tick',lambda: np.sin(2*np.pi*2400*t(.03))*np.exp(-t(.03)*220)+.4*fftf(noise(.03),4000)*np.exp(-t(.03)*300))
mk('click',lambda: np.sin(2*np.pi*1500*t(.05))*np.exp(-t(.05)*120)+.5*fftf(noise(.05),3000)*np.exp(-t(.05)*250))
mk('type',lambda: fftf(noise(.04),1500,7000)*np.exp(-t(.04)*160)+.4*np.sin(2*np.pi*600*t(.04))*np.exp(-t(.04)*200))
mk('tap',lambda: np.sin(2*np.pi*180*t(.12))*np.exp(-t(.12)*40)+.6*fftf(noise(.12),1500)*np.exp(-t(.12)*120))
mk('ding',lambda: bell([1318.5,1975.5,2637,3951],1.4,3.5))
mk('cash',lambda: np.concatenate([bell([2093,3136],.09,20),bell([2637,3951,5274],1.3,3.2)]))
mk('ping',lambda: np.concatenate([bell([1046.5,2093],.12,15),bell([1568,3136],.7,6)]))
mk('notify',lambda: np.concatenate([bell([880,1760],.11,14),bell([1174.7,2349],.11,14),bell([1568,3136],.8,5)]))
mk('success',lambda: seqmix([(i*.08,bell([f,f*2],.9,5)) for i,f in enumerate([1046.5,1318.5,1568,2093])],1.3))
mk('shimmer',lambda: seqmix([(i*.045,bell([f],.8,4.5)) for i,f in enumerate([2093,2637,3136,3951,4186,5274,6271])],1.4))
mk('lock',lambda: np.sign(np.sin(2*np.pi*1760*t(.07)))*.3*np.exp(-t(.07)*40))
mk('lock_confirm',lambda: np.concatenate([np.sign(np.sin(2*np.pi*1760*t(.07)))*.3,np.zeros(int(.03*SR)),np.sin(2*np.pi*2637*t(.35))*np.exp(-t(.35)*9)]))
mk('nope',lambda: np.sign(np.sin(2*np.pi*220*t(.16)))*.4*np.exp(-t(.16)*14)+np.sin(2*np.pi*110*t(.16))*np.exp(-t(.16)*14))
def kick(d=.6,f0=160,f1=40,dec=7): return sine_sweep(f0,f1,d,3)*np.exp(-t(d)*dec)
mk('impact',lambda: 1.2*kick(1.2,120,32,3.5)+.6*fftf(noise(1.2),0,1800)*np.exp(-t(1.2)*7)+.25*fftf(noise(1.2),3000)*np.exp(-t(1.2)*18))
mk('impact_soft',lambda: kick(.45,180,55,9)+.25*fftf(noise(.45),0,3000)*np.exp(-t(.45)*20))
mk('boom',lambda: 1.3*kick(1.8,90,26,2.2)+.5*fftf(noise(1.8),0,600)*np.exp(-t(1.8)*3))
mk('stamp',lambda: kick(.5,220,60,10)+.8*fftf(noise(.5),200,5000)*np.exp(-t(.5)*22))
mk('glitch',lambda: np.concatenate([fftf(noise(.05),R.uniform(200,800),R.uniform(3000,9000))*(R.random()>.3) for _ in range(9)])*np.repeat(R.choice([.3,1],9),int(.05*SR)))
mk('riser',lambda: (svf(noise(1.0),300+7000*(t(1.0))**2.5,2)+.5*np.sin(2*np.pi*np.cumsum(200+900*t(1.0)**2)/SR))*t(1.0)**2)
mk('riser_short',lambda: svf(noise(.5),500+5000*(t(.5)/.5)**2,2)*(1-t(.5)/.5)**.5)
mk('rise_tone',lambda: np.sin(2*np.pi*np.cumsum(300+500*t(2.0)/2)/SR)*.4*np.sin(np.pi*t(2.0)/2))
mk('powerdown',lambda: np.sin(2*np.pi*np.cumsum(np.maximum(40,700*(1-t(.7)/.7)**2))/SR)*np.exp(-t(.7)*3)+.3*fftf(noise(.7),0,1500)*np.exp(-t(.7)*8))
mk('fall_small',lambda: np.sin(2*np.pi*np.cumsum(1200-900*t(.5)/.5)/SR)*.6*np.sin(np.pi*t(.5)/.5))
mk('fall',lambda: np.sin(2*np.pi*np.cumsum(1800-1600*(t(.5)/.5)**.7)/SR)*np.sin(np.pi*t(.5)/.5)**.5+.5*svf(noise(.5),4000-3500*t(.5)/.5,2))


mk('soft_whoosh',lambda: svf(noise(.5),300+2200*np.sin(np.pi*t(.5)/.5)**2,.9)*np.sin(np.pi*t(.5)/.5)**2)
mk('swipe_up',lambda: SFX['whoosh_up'])
mk('letters',lambda: seqmix([(i*.04,(np.sin(2*np.pi*(1800+i*90)*t(.03))*np.exp(-t(.03)*200))) for i in range(9)],.5))
mk('select',lambda: np.concatenate([np.sin(2*np.pi*1320*t(.05))*np.exp(-t(.05)*60),np.sin(2*np.pi*1760*t(.12))*np.exp(-t(.12)*30)]))
mk('toggle',lambda: .8*np.sin(2*np.pi*900*t(.04))*np.exp(-t(.04)*150)+.6*fftf(noise(.04),2000)*np.exp(-t(.04)*250)+np.pad(np.sin(2*np.pi*600*t(.04))*np.exp(-t(.04)*150),(int(.05*SR),0))[:int(.04*SR)])
mk('msg',lambda: np.concatenate([bell([1568,3136],.1,18),bell([2093,4186],.45,9)]))
mk('thud',lambda: kick(.7,110,38,6)+.3*fftf(noise(.7),0,900)*np.exp(-t(.7)*12))
mk('thud_small',lambda: kick(.35,140,50,10))
mk('sparkle',lambda: seqmix([(i*.03,bell([3000+i*400],.4,9)) for i in range(8)],.8))
mk('deep',lambda: kick(1.4,70,30,2.6)+.2*fftf(noise(1.4),0,400)*np.exp(-t(1.4)*3))

# ---------- trilha ----------
T=json.load(open('build/timeline.json'));TOT=T['total'];N=int((TOT+1)*SR)
st={s['id']:s['start'] for s in T['scenes']}
tense0,tense1,cta0=st['s5'],st['s9'],st['s16']
mus=np.zeros(N);bpm=120;beat=60/bpm
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
m2f=lambda m:440*2**((m-69)/12)
def add(buf,x,at):
    i=int(at*SR); x=x[:max(0,len(buf)-i)]; buf[i:i+len(x)]+=x
kickS=kick(.35,150,45,12); hat=fftf(noise(.05),7000)*np.exp(-t(.05)*90); clap=fftf(noise(.18),900,5000)*np.exp(-t(.18)*25)
b=0.0;k=0
while b<TOT:
    inT=tense0<=b<tense1; bar=int(b/(beat*4)); ch=chords[(bar//2)%4]
    if inT:
        if k%2==0: add(mus,kickS*.9*(.6+.4*(k%4==0)),b)   # pulso tipo batimento
    else:
        add(mus,kickS,b)
        if k%4 in(1,3): add(mus,clap*.35,b)
        add(mus,hat*.25,b+beat/2); add(mus,hat*.12,b)
        # baixo
        f=m2f(ch[0]-24); tb=t(beat*.9); add(mus,.5*np.sin(2*np.pi*f*tb)*np.exp(-tb*3)+.15*np.sin(4*np.pi*f*tb)*np.exp(-tb*5),b)
    k+=1;b+=beat
# pad
pad=np.zeros(N);tt=np.arange(N)/SR
for bar in range(int(TOT/(beat*8))+2):
    t0=bar*beat*8; ch=chords[bar%4]; seg=t(beat*8+.5)
    x=sum(np.sin(2*np.pi*m2f(m)*(1+dt)*seg) for m in ch for dt in(-.003,.003))
    x*=np.minimum(1,seg/.4)*np.minimum(1,(beat*8+.5-seg)/.5)
    add(pad,x*.08,t0)
mus+=pad
# arpejo cintilante na parte "solução"
for i,b in enumerate(np.arange(tense1,cta0,beat/2)):
    ch=chords[(int(b/(beat*4))//2)%4];f=m2f(ch[i%3]+12);add(mus,.06*np.sin(2*np.pi*f*t(.25))*np.exp(-t(.25)*12),b)
# volume por seção
g=np.ones(N); g[(tt>=tense0)&(tt<tense1)]=.75
fade=np.clip((TOT+.5-tt)/2.0,0,1); g*=fade; g[:int(.5*SR)]*=np.linspace(0,1,int(.5*SR))
mus=norm(mus,1)*g

# ---------- voz ----------
v,vsr=sf.read('build/voice.wav'); vt=np.arange(int(len(v)/vsr*SR))/SR; voice=np.interp(vt,np.arange(len(v))/vsr,v)
voice=np.pad(voice,(0,max(0,N-len(voice))))[:N]
# leve presença: realce de agudos
voice=voice+.25*fftf(voice,2500,9000); voice=norm(voice,1)
# ducking
e=np.abs(voice); w=int(.15*SR); e=np.convolve(e,np.ones(w)/w,'same'); duck=1-.55*np.clip(e/ (e.max()*.25),0,1)
# ---------- sfx ----------
sfx=np.zeros(N); cues=json.load(open('build/cues.json')); missing=set()
for c in cues:
    x=SFX.get(c['type'])
    if x is None: missing.add(c['type']);continue
    add(sfx,x*c['g'],max(0,c['t']))
print('faltando:',missing,'cues:',len(cues))
mix=1.0*voice+.16*mus*duck+.42*sfx
mix=np.tanh(mix*1.1)/np.tanh(1.1)
mix=norm(mix,.97)
sf.write('build/mix.wav',np.stack([mix,mix],1).astype(np.float32),SR)
print('ok',len(mix)/SR)
