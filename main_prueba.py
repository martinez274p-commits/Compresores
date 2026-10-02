from machine import UART,Pin,ADC
import machine
import time
import mod485
from random import randint
tiempo=time.ticks_ms()
cambio=0
enviar=0
RUN=Pin(12,Pin.OUT)
RUN.value(1)

def data_485(a,d,m): #dat=01030000002 d=direccion de esclavo m=nombre de modulo esclavo "PR", "SC", "M2" , "AL", "MS", "MW"
    time_out=200
    mod485.send_data(a)
    time_init=time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(),time_init)<time_out:
        if mod485.rs485_available():
            data=mod485.read_rs485(d,m)
            return data
    return 0,0,0,0,0,0

dat="0210001000020002" #secadores
dir_e=2
m_name="SC"
print(data_485(dat,dir_e,m_name))
time.sleep_ms(1000)
#dir  1 punto de rocio  2 secadores   3 motor2   4 motor3   5 motor4   8 alarmas  9 microsd  10 nube

"""
while True:
    if time.ticks_diff(time.ticks_ms(),tiempo)>1000:
        #dat=b'\x01\x04\x00\x00\x00\x03'
        if cambio==0:
            #dat="010400000003"
            dat="030300000005" #motor2
            dir_e=3
            m_name="M2"
            #dat="030400100000" 
            cambio=1
        elif cambio==1:
            contador=[randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1),randint(0,1)]
            enviar=0
            for i in range(4):
                enviar=enviar+contador[i]*(2**i)
            #print(contador,enviar)
            dat="08040000"+f'{enviar:04x}' #alarmas
            dir_e=8
            m_name="AL"
            cambio=2
        elif cambio==2:
            dat="010400000003"
            dir_e=1
            m_name="PR"
            cambio=3
        else:
            dat="0203000000010003" #secadores
            dir_e=2
            m_name="SC"
            cambio=0
        print(data_485(dat,dir_e,m_name))
        tiempo=time.ticks_ms()"""
while True:
    if time.ticks_diff(time.ticks_ms(),tiempo)>1000:
        #dat=b'\x01\x04\x00\x00\x00\x03'
        dat="010300000004"
        dir_e=1
        m_name="PR"
        print(data_485(dat,dir_e,m_name))
        tiempo=time.ticks_ms()