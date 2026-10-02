#import main_bomba_v5_nfpa_rev
import machine
import time
import mod485
tiempo=time.ticks_ms()
cambio=0
while True:
    if time.ticks_diff(time.ticks_ms(),tiempo)>1000:
        #dat=b'\x01\x04\x00\x00\x00\x03'
        if cambio==0:
            dat="010400000003"
            cambio=1
        else:
            dat="0203000000020000"
            cambio=0 
        mod485.send_data(dat)
        tiempo=time.ticks_ms()
        tiempo_resp=time.ticks_ms()
    if mod485.rs485_available():
        print(mod485.read_rs485(1,"PR"),"tiempo resp:",time.ticks_ms()-tiempo_resp)