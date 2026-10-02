#import main_bomba_v5_nfpa_rev
import machine
import time
import mod485
from random import randint
tiempo=time.ticks_ms()
cambio=0
enviar=0
while True:
    if time.ticks_diff(time.ticks_ms(),tiempo)>1000:
        #dat=b'\x01\x04\x00\x00\x00\x03'
        if cambio==0:
            dat="010400000003"
            cambio=1
        elif cambio==1:
            contador=[randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1)]
            enviar=0
            for i in range(10):
                enviar=enviar+contador[i]*(2**i)
            #print(contador,enviar)
            dat="04040000"+f'{enviar:04x}'
            cambio=2
        else:
            dat="020300000004"
            cambio=0
        mod485.send_data(dat)
        tiempo=time.ticks_ms()
        tiempo_resp=time.ticks_ms()
    if mod485.rs485_available():
        print(mod485.read_rs485(),"tiempo resp:",time.ticks_ms()-tiempo_resp)