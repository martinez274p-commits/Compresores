def run():
    from machine import UART,Pin,ADC
    from time import ticks_ms, ticks_diff, sleep_ms
    import data_value
    import mod485_secador
    secador=data_value.DATA()

    Secador1=Pin(23,Pin.OUT) #out rele
    Secador2=Pin(22,Pin.OUT) #out rele
    
    AlarmaPR=Pin(19,Pin.OUT) #out rele 19
    AlarmaCO=Pin(21,Pin.OUT) #out rele
     
    Sec1=Pin(25,Pin.IN)      #in dig
    Sec2=Pin(33,Pin.IN)      #in dig
    
    SecR_1=Pin(39,Pin.IN)      #in dig
    SecR_2=Pin(34,Pin.IN)      #in dig
    
    Secador1.value(0)
    Secador2.value(0)
    adc36 = ADC(Pin(36))#adc 36 
    adc36.atten(ADC.ATTN_0DB)
    param=secador.lectura_adc()
    alertas=secador.lectura_alertas()
    dir_hex=secador.lectura_dir()
    fabrica=secador.lectura_fabrica()
    print("adc", param)
    print("alertas", alertas) #CO Y PR
    print("dir", dir_hex)
    print("fabrica", fabrica)
    accion=[0,0,0,0]
    co=0
    #sleep_ms(5000)
    if Sec1.value()==0 and Sec2.value()==0:
        secador_en_uso="0"
    if Sec1.value()==1 and Sec2.value()==1:
        secador_en_uso="3"
    if Sec1.value()==1 and Sec2.value()==0:
        secador_en_uso="1"
    if Sec1.value()==0 and Sec2.value()==1:
        secador_en_uso="2"
    torre_en_uso="A"
    time_auto=ticks_ms()
    time_run=time_auto
    tiempo_auto=20000
    enviar=""
    PR=0
    cambio=0
    datos=[0,0,0]
    pr_seg=2
    dif=0
    adc_c=0
    contador=0
    #rxc=Pin(16,Pin.IN)
    #rxc.value(0)
    while True:
        for i in range(100):
            adc_c=adc_c+adc36.read()
        adc_c=adc_c/100
        co=int(((adc_c-param[0])*param[2])/param[1])
        #sleep_ms(1000)
        #print(co,adc_c)
        if PR>alertas[1]:
            AlarmaPR.value(1)
        else:
            AlarmaPR.value(0)
        if co>alertas[0]:
            AlarmaCO.value(1)
        elif co<alertas[0]:
            AlarmaCO.value(0)
        if mod485_secador.rs485_available():
            accion=mod485_secador.read_rs485(dir_hex,cambio)
            #print("CO",co,"PR",PR)
            if accion[0]==1 or accion[0]==2 or accion[0]==3 or accion[0]==4 or accion[0]==5:
                time_run=ticks_ms()
                cambio=0
            if cambio==1:
                if accion[0]==6:
                    PR=(accion[1]/10)
                    #print("PR:",PR)
            if cambio==0:
                if accion[0]==1:
                    PR=accion[1]
                    dat="0"+str(dir_hex)+"03"+f'{Sec1.value():02x}'+f'{Sec2.value():02x}'+f'{co & 0xFFFF:04x}'+f'{PR & 0xFFFF:04x}'
                    PR=(accion[1]/10)
                    mod485_secador.send_data(dat)
                    Secador1.value(accion[2])
                    Secador2.value(accion[3])
                if accion[0]==2: #cambio de ID
                    dir_hex=accion[1]
                    secador.guardar_dir(dir_hex)
                    dat="0"+str(dir_hex)+"1000100002"
                    mod485_secador.send_data(dat)
                if accion[0]==3: #cambio de adc
                    dat="0"+str(dir_hex)+"1000200002"
                    param[:]=accion[1:4]
                    secador.guardar_adc(param)
                    mod485_secador.send_data(dat)
                if accion[0]==4: #cambio de alertas
                    dat="0"+str(dir_hex)+"1000250002"
                    alertas[:]=accion[1:3]
                    secador.guardar_alertas(alertas)
                    mod485_secador.send_data(dat)
                if accion[0]==5: #cambio de alertas
                    dat="0"+str(dir_hex)+"1000300003"
                    param[:]=fabrica[0:3]
                    alertas[:]=fabrica[3:5]
                    dir_hex=fabrica[5]
                    secador.guardar_adc(param)
                    secador.guardar_dir(dir_hex)
                    secador.guardar_alertas(alertas)
                    mod485_secador.send_data(dat)
        elif ticks_diff(ticks_ms(),time_run)>tiempo_auto:
            contador=contador+1
            sleep_ms(1)
            if contador>=5000:
                cambio=1
                print("enviar_485")
                dat="010400000003"
                mod485_secador.send_data(dat) #enviar peticion de punto de rocio a sensor
                contador=0
                if SecR_1.value()==1:
                    Secador1.value(1)
                    Secador2.value(0)
                elif SecR_2.value()==1:
                    Secador1.value(0)
                    Secador2.value(1)
                else:
                    Secador1.value(1)
                    Secador2.value(1)
#run()