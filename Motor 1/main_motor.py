def run():
    from machine import UART,Pin,ADC
    from time import ticks_ms, ticks_diff, sleep_ms
    import motor485
    
    pines = {"ACT": 25, "SOB": 33,"TEM": 32, "ENT": 35, "AUT": 4, "D1": 13, "D2": 14,"D3": 27,"D4": 26} 
    dir_pin = ["ACT", "SOB", "TEM", "ENT", "AUT", "D1", "D2", "D3", "D4"]
    gpin = {nombre: Pin(pin, Pin.IN) for nombre, pin in pines.items()}
    PIN=[0,0, 0,0, 0,0, 0,0, 0]
    PIN_IN = [gpin[n].value() for n in dir_pin]
    
    motor=Pin(23,Pin.OUT)
    out24=Pin(22,Pin.OUT)
    RUN=Pin(12,Pin.OUT)
    RUN.value(0)
    
    motor.value(0)
    out24.value(0)
    da=""
    d_h=""
    RUN.value(1)
    time_run=ticks_ms()
    tiempo_off=10000
    contador=0
    while True:
        dir_hex=PIN_IN[5]+(PIN_IN[6]*2)+(PIN_IN[7]*4)+(PIN_IN[8]*8)
        d_h="0"+str(dir_hex) if dir_hex<=9 else str(dir_hex)
        PIN_IN = [gpin[n].value() for n in dir_pin]
        if motor485.rs485_available():
            accion=motor485.read_rs485(dir_hex)
            RUN.value(1)
            if accion[0]==1 or accion[0]==2:
                time_run=ticks_ms()
            if accion[0] == 1: #lectura de parametros
                da=""
                dat=str(d_h)+"03"+f'{PIN_IN[0]:02x}'+f'{PIN_IN[1]:02x}'+f'{PIN_IN[2]:02x}'+f'{PIN_IN[3]:02x}'+f'{PIN_IN[4]:02x}'
                print(accion[1],dat)
                motor.value(accion[1])
                out24.value(accion[2])
                motor485.send_data(dat)
            if accion[0] == 2:
                motor.value(accion[1])
                out24.value(accion[2])
                dat=str(d_h)+"0400100"+str(accion[1])+"0"+str(accion[2])
                motor485.send_data(dat)
        elif ticks_diff(ticks_ms(),time_run)>tiempo_off:
            sleep_ms(1)
            contador=contador+1
            contador=0 if contador>=1000 else contador
            if contador==0: 
                RUN.value(0)
            if contador==500:
                RUN.value(1)
            motor.value(0)
            out24.value(0)
#run()