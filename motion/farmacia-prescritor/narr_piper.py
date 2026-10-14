import json,re,numpy as np,soundfile as sf,sherpa_onnx
d="/tmp/claude-0/piper/vits-piper-pt_BR-dii-high"
tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f"{d}/pt_BR-dii-high.onnx",tokens=f"{d}/tokens.txt",data_dir=f"{d}/espeak-ng-data",noise_scale=0.6,noise_scale_w=0.7,length_scale=1.0),num_threads=4)))
SPEED=1.13
# cena -> frases (falado, legenda, pausa depois em s)
S=[
("s1",[("Se você tem uma farmácia de manipulação,","Se você tem uma farmácia de manipulação,",.25),("que fatura mais de oitenta mil reais por mês...","que fatura mais de R$ 80 mil por mês...",.45)]),
("s2",[("quero te apresentar um novo tipo de prescritor.","quero te apresentar um novo tipo de prescritor.",.35),("Ele trabalha vinte e quatro horas,","Ele trabalha 24 horas,",.15),("sete dias por semana,","7 dias por semana,",.2)]),
("s3",[("não pede comissão,","não pede comissão,",.2)]),
("s4",[("e manda paciente direto pro seu WhatsApp,","e manda clientes direto pro seu WhatsApp,",.15),("com a receita na mão.","com a receita na mão.",.6)]),
("s5",[("Mas antes,","Mas antes,",.2),("me responde uma coisa.","me responde uma coisa:",.5)]),
("s6",[("Quantos prescritores você tem hoje?","Quantos prescritores você tem hoje?",.35),("Dois?","Dois?",.25),("Cinco?","Cinco?",.25),("Dez?","Dez?",.55)]),
("s7",[("E se um deles parar de te indicar amanhã,","E se um deles para de te indicar amanhã,",.2),("o que acontece com o seu faturamento?","o que acontece com o seu faturamento?",.55)]),
("s8",[("Despenca.","Despenca.",.35),("Correto?","Correto?",.65)]),
("s9",[("Por isso, a gente criou o Método Púlse.","Por isso criamos o Método PULLSE.",.35)]),
("s10",[("Um sistema que captura quem já procura uma fórmula,","um sistema que captura quem já está procurando por uma fórmula,",.25),("e leva essa pessoa direto pro WhatsApp da farmácia,","e leva essa pessoa direto pro WhatsApp da farmácia,",.15),("pronta pra orçar.","pronta pra orçar.",.55)]),
("s11",[("Sem médico novo.","Sem médico novo.",.25),("Sem panfleto.","Sem panfleto.",.3),("E tudo dentro da regulação da Anvisa.","Tudo dentro da regulação da Anvisa.",.55)]),
("s12",[("É isso que a gente faz na Impúlse.","É exatamente isso que fazemos na Inpullse.",.4)]),
("s13",[("Já são mais de cinquenta e três milhões em faturamento,","Já geramos mais de R$ 53 milhões em faturamento,",.1),("pra negócios locais.","pra negócios locais.",.35)]),
("s14",[("E a gente sabe fazer isso funcionar,","e sabemos como fazer isso funcionar,",.15),("pra sua farmácia de manipulação.","pra sua farmácia de manipulação.",.6)]),
("s15",[("Se você quer parar de depender de prescritor,","Se você quer parar de depender de prescritor,",.25),("e ter um fluxo previsível de clientes chegando todo dia...","e ter um fluxo previsível de clientes chegando todo dia,",.45)]),
("s16",[("Clica no link aqui embaixo,","clica aqui nesse link,",.2),("preenche o formulário,","preenche um formulário rápido",.15),("e um especialista te chama pra explicar o passo a passo.","e um dos nossos especialistas te explica o passo a passo.",1.5)]),
]
def est_words(cap,t0,dur):
    ws=cap.split();wt=[]
    for w in ws:
        b=len(re.sub(r'[^\wÀ-ú$]','',w))+1.5
        if re.search(r'\d',w):b+=8
        wt.append(b)
    k=dur/sum(wt);t=t0;out=[]
    for w,b in zip(ws,wt):out.append(dict(w=w,t0=round(t,3),t1=round(t+b*k,3)));t+=b*k
    return out
SR=22050;t=.45;scenes=[];buf=[]
for sid,phr in S:
    st=t;words=[];caps=[]
    for spk,cap,pause in phr:
        a=tts.generate(spk,sid=0,speed=SPEED);x=np.array(a.samples,dtype=np.float32)
        idx=np.where(np.abs(x)>0.01)[0];x=x[max(idx[0]-150,0):idx[-1]+300]
        dur=len(x)/SR;buf.append((t,x));words+=est_words(cap,t,dur);caps.append(cap);t+=dur+pause
    scenes.append(dict(id=sid,start=round(st,3),voice=round(t-st-phr[-1][2],3),caption=' '.join(caps),words=words))
total=t+.3
for i,o in enumerate(scenes):o['end']=round(scenes[i+1]['start'] if i+1<len(scenes) else total,3)
B=np.zeros(int(total*SR)+SR,dtype=np.float32)
for s0,x in buf:i=int(s0*SR);B[i:i+len(x)]+=x
sf.write('build/voice.wav',B,SR)
json.dump(dict(total=round(total,3),scenes=scenes),open('build/timeline.json','w'),ensure_ascii=False,indent=1)
open('build/timeline.js','w').write('const TIMELINE='+open('build/timeline.json').read()+';')
print('total',round(total,2));[print(s['id'],s['start'],s['voice']) for s in scenes]
