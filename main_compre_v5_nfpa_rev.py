def run(): 
    from machine import Pin
    from time import sleep_ms, ticks_ms, ticks_diff
    import configuracion as display
    import math
    ventanas=0 #0 normal 1 presiones 2 sensores 3 unidades 4 historial
    config_value=0
    config_sen=0
    borrar_time=0
    fecha=0
    pt=display.leer_parametros()
    print("param:",pt)
    claves=["R","1123","SIIM","1296","",""]
    clav_m=["RSIIM","11231296","","","",""]
    verf=0
    Fecha=""
    retardo=pt[20]
    rst=[0,0]
    pines = {"S1": 33, "EM1": 25, "AUTO": 4,"TEMP": 32} 
    dir_pin = ["S1", "EM1", "AUTO", "TEMP"]
    dir_en_hmi=["","presiones","sensores"]
    dir_alert=["Unidad 1 falla termica","Unidad 2 falla termica",
                "Unidad 1 en sobrecarga","Unidad 2 en sobrecarga",
                "Respaldo Unidad 1","Respaldo Unidad 2",
                "Retardo, Unidad 1 no activado","Retardo, Unidad 2 no activado",
                "Presion de salida baja","Presion de salida alta","Presion de tanque baja","Presion de tanque alta",
                "Retardo, unidades encendidas","Retardo, Cambio de unidad","Punto de rocio alto","Alerta de CO",
                "Punto de Rocio sin conexion","Modulo PR y CO sin conexion","Modulo M2 sin conexion","Modulo alarmas sin conexion",
                "Mem_Ext sin conexion","Mem_SD no conectada","Modulo WiFi fallo"] #23
    alpha=float(pt[17])#0.01#0.012
    adc_presion=[0,0]
    adc_filtrado=[0,0]
    alerta=     [0,0,0,0,0 ,0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0] #23 alertas
    alerta2=    [0,0,0,0,0 ,0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0] #23 alertas
    alerta_hist=[0,0,0,0,0 ,0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0] #23 alertas
    PIN1=[0,0,0,0]
    PIN2=[0,0,0,0]
    #mod_enviar="M1,0,M2,0"
    io = {nombre: Pin(pin, Pin.IN, Pin.PULL_DOWN) for nombre, pin in pines.items()}
    PIN1 = [io[n].value() for n in dir_pin] #lectura de pines controlador
    buzz=Pin(22,Pin.OUT)
    Motor1=Pin(23,Pin.OUT)
    presiones=display.leer_presiones()
    sensores=display.leer_sensores()
    time_disp=pt[19]
    time_disp_ult=ticks_ms()
    time_peticion=ticks_ms()
    time_b2=ticks_ms()
    cambio_modulo=0
    tiempos=[display.lectura_tiempo(1),display.lectura_tiempo(2)]
    print(tiempos)
    timing1=[0,tiempos[0],0,display.time_format(tiempos[0][0],0)] #inicio hora, hora, guardar, formato(hora a ceros, contador,hora hmi)
    timing2=[0,tiempos[1],0,display.time_format(tiempos[1][0],0)] #inicio hora, hora, guardar, formato(hora a ceros, contador,hora hmi)
    hmi_time=[timing1[3][2],timing2[3][2]]
    print(timing1)
    #time_uni1=[init_hour1,h[0],save_time1,h_data1] 
    print("presiones",presiones)
    print("sensores",sensores)
    tiempo_bombas=ticks_ms()
    time_buzz=(int(presiones[6])*60)*1000 #tiempo sil
    timer_limit=(presiones[5]*60)*1000 #tiempo refuerzo
    #paro_bombas=(int(presiones[6])*60)*1000 #tiempo enc
    mod=1
    PIN=PIN1+PIN2
    modos=[PIN[2],PIN[6]]
    t_paro=[PIN[3],PIN[7]]
    ult_modos=modos
    cambio_motor=1
    #menor_uni=display.obtener_menor_tiempo(tiempos=hmi_time)
    print("cambio_motor1",cambio_motor)
    #print("tiempos unidades:",hmi_time)
    #print("unidad menor tiempo:",menor_uni)
    
    sleep_ms(5000)
    
    cont_enc_units=[0,0,0]
    bloqueo_units=[0,0,0]
    ult_cambio_motor=cambio_motor
    #cont_ciclos=0
    ciclos=2
    #if cont_ciclos<ciclos:
    cambio_motor=display.rect_cambio(cambio_motor,modos,display.obtener_menor_tiempo(hmi_time,mod,modos))
    #    ult_cambio_motor=cambio_motor
    #if cambio_motor!=ult_cambio_motor:
    #    cont_ciclos=cont_ciclos+1
    print("cambio_motor2",cambio_motor)
    c_m=display.operacion(modos,cambio_motor,mod) #automatico,arranque,modo
    cambio_motor=c_m[0]
    mod_enviar=c_m[1]
    mod_env2=mod_enviar.replace(",1",",0")
    dir_param=["min_hosp","high_hosp","","min_tanque","high_tanque"]
    sec_c=["apagado","encendido"]
    dir_sec_c=["sec_1","sec_2"]
    dir_mot_c=["manualoff","manualon"]
    print("cambio_motor3",cambio_motor)
    print("mod_enviar",mod_enviar)
    Temp=[32,12,43] #val hmi
    presion=[10,10]
    conta=[0,0,0]
    conta_ult=[0,0,0]
    init_time=[0,0,0]
    refuerzo=[0,0,0]
    h=[0,0]
    timings=[timing1,timing2]
    data_valor=[presion[0],presion[1]] #hosp,tanq
    dir_adc=[0,1]
    START=1
    START_UNI=0
    timer=ticks_ms()
    time_rs4851=ticks_ms()
    time_rs4852=ticks_ms()
    estado=0
    AG,AT,AR,AH=0,0,0,0
    ref_cambio=0
    retar=0
    buzzer=0
    verf1=0
    verf2=0
    rest=1
    cambio_p=0
    cont_retar=0
    cont_pub_estado=0
    dat_rs=[0,0]
    for i in range(5):
        display.write_HMI("set_text","label",dir_param[i],str(presiones[i])) if i!=2 else None
    display.set_color("tanque_psi","text_color",0x44,0x44,0x44,0xff)
    display.set_color("hosp_psi","text_color",0x44,0x44,0x44,0xff)
    ciclo=0
    #for i in range(3):
    #    display.write_HMI("set_text","label",f"T_{i+1}","T.Stop "+str(int(paro_bombas/1000))+"s = 0s T.On")
    #timer_out_bomb=(presiones[5]+int(presiones[6]))*2 #tiempo de seguridad de apagado de bombas
    #timer_out_bomb=60 if timer_out_bomb>60 else timer_out_bomb
    #timer_out_bomb=timer_out_bomb*60*1000
    cambio_prco=0
    punto_rocio=0
    mono=0
    dir_bar=[punto_rocio,mono]
    init_sec="02030000"
    dir_modulo_485=["010400000003",init_sec,"030300000005","08040000"]
    name_modulo=["PR","SC","M2","AL"]
    modo_master=[0,0,0,0]
    mod_ing=0
    verfm=0
    info_485=[0,0]
    config_mod=1
    Sec_1=1
    Sec_2=0
    sec=[0,0]
    man=[0,0]
    while True:
        dir_modulo_485[1]=init_sec+f'{Sec_1 & 0XFFFF:02x}'+f'{Sec_2 & 0XFFFF:02x}'
        for i in range(0,2):
            adc_presion[i]=display.adc(i)
            adc_filtrado[i]=(alpha*adc_presion[i])+((1-alpha)*adc_filtrado[i])
        PIN1 = [io[n].value() for n in dir_pin] #lectura de pines controlador
        PIN=PIN1+PIN2
        if ticks_diff(ticks_ms(),time_peticion)>pt[21]:
            enviar=0
            if cambio_modulo==3: #modulo alarmas
                rel=[AG,AR,AT,0,0, 0,0,0,0,0] #posiciones de rele izquierda - derecha -> Z
                for i in range(10):
                    enviar=enviar+rel[i]*(2**i)
            env_pral=[0,int(punto_rocio*10),0,enviar]
            dat=dir_modulo_485[cambio_modulo] if cambio_modulo!=1 and cambio_modulo!=3 else dir_modulo_485[cambio_modulo] + f'{env_pral[cambio_modulo] & 0XFFFF:04x}'
            dir_e=cambio_modulo+1 if cambio_modulo!=3 else 8
            m_name=name_modulo[cambio_modulo]
            cambio_modulo=cambio_modulo+1 if cambio_modulo<3 else 0
            time_peticion=ticks_ms()
            #print("enviar data",dat,dir_e,m_name)
            info_485=display.data_485(dat,dir_e,m_name)
            #print("data",pt[10])
            print(info_485)
            for i in range(len(name_modulo)):
                if m_name==name_modulo[i] and info_485[0]==0 and pt[10]==1:
                    alerta[i+16]=1
            if info_485[0]==1: #punto de rocio y co
                #punto_rocio=info_485[1]
                b1=243.04
                a1=17.625
                #print(info_485)
                H=info_485[2]-pt[25]
                T=info_485[3]-pt[24]
                try:
                    punto_rocio=int(((b1*((math.log(H/100))+((a1*T)/(b1+T))))/(a1-math.log(H/100)-(a1*(T/(b1+T)))))*10)/10
                except:
                    pass
                #print("val_punto",punto_rocio,info_485[1])
                #punto_rocio=info_485[1]
                alerta[16]=0
            if info_485[0]==2: #secadores
                #PR=info_485[1] #dato de PR enviado y recibido
                mono=info_485[2] #dato de co
                sec=[info_485[3],info_485[4]] #secador 1 y secador 2
                alerta[17]=0
                #print(info_485)
            if info_485[0]==3: #tarjeta motor
                #print("tarjeta motor:",info_485)
                PIN2[1]=info_485[3] #contactor motor 2
                PIN2[0]=info_485[2] #sobrecarga motor 2
                #PIN2[0]=info_485[1] #temperatura motor 2
                PIN2[2]=info_485[4] #automatico motor 2
                PIN2[3]=info_485[5] #pin dig motor 2
                alerta[18]=0
            if info_485[0]==8:
                modulo_alarmas=1
                alerta[19]=0
            PIN=PIN1+PIN2

        if display.available()>0:
            dato=display.read_HMI()
            print(dato)
            if len(dato)==2:
                if dato[0]=="silenciar":
                    silencio=1
                    buzz.value(1) #buzzer on
                    sleep_ms(400)
                    buzz.value(0) #buzzer off
                    time_b2=ticks_ms()
                    if cont_retar<1:
                        cont_retar=cont_retar+1
                    else:
                        cont_retar=0
                        for i in range(4,8): #retardos y respaldos
                            alerta[i]=0
                        alerta[12]=0 #retardo todas  las unidades encendidas
                        alerta[13]=0 #retardo cambio de unidad
                        AR=0
                if dato[0]=="conf_sec":
                    display.open_win("pop_secadores")
                    display.write_HMI("set_image","image","sec_1",str(sec_c[Sec_1]))
                    display.write_HMI("set_image","image","sec_2",str(sec_c[Sec_2]))
                    
                if dato[0]=="sec1" and Sec_1==0:
                    Sec_1=1
                    display.write_HMI("set_image","image","sec_1",str(sec_c[Sec_1]))
                elif dato[0]=="sec1" and Sec_1==1:
                    Sec_1=0
                    display.write_HMI("set_image","image","sec_1",str(sec_c[Sec_1]))
                if dato[0]=="sec2" and Sec_2==0:
                    Sec_2=1
                    display.write_HMI("set_image","image","sec_2",str(sec_c[Sec_2]))
                elif dato[0]=="sec2" and Sec_2==1:
                    Sec_2=0
                    display.write_HMI("set_image","image","sec_2",str(sec_c[Sec_2]))
                    
                if dato[0]=="btn1":
                    modo_master=[1,0,0,0] if modo_master[0]==0 else [0,0,0,0]
                if dato[0]=="btn2":
                    modo_master=[0,1,0,0] if modo_master[0]==1 else [0,0,0,0]
                if dato[0]=="btn3":
                    modo_master=[0,0,1,0] if modo_master[1]==1 else [0,0,0,0]
                if dato[0]=="btn4":
                    modo_master=[0,0,0,1] if modo_master[2]==1 else [0,0,0,0]
                if modo_master[3]==1:
                    modo_master=[0,0,0,0]
                    display.open_win("user")
                    config_mod=1
                    #display.menu_ing(pt)
                if config_mod==1:
                    verfm=display.verificar_user(dato,clav_m,2)
                    if dato[0]=="cancelar":   
                        display.close_win("user")   
                        config_mod=0
                if verfm==1:
                    display.open_win("conf_param")
                    display.menu_ing(pt)
                if ventanas==0:
                    ventanas=display.menu_hmi(dato,presiones,sensores,ventanas)
                if ventanas==1:
                    if fecha==2:
                        Fecha=display.config_fecha(dato,Fecha)
                        if dato[0]=="atras_fecha":
                            display.close_win("Fecha")
                            fecha=0
                        display.guardar_fecha(Fecha) if dato[0]=="guardar_fecha" else None
                    if fecha==1:
                        Fecha=display.disp_fecha(dato)
                        fecha=2
                    if config_value==1:
                        verf=display.verificar_user(dato,claves,2)
                        if dato[0]=="cancelar":   
                            display.close_win("user")   
                            config_value=0
                    presiones=display.edit_presiones(presiones,dato) if config_value==2 else presiones
                    if dato[0]=="edit_pre":
                        display.open_win("user")
                        config_value=1
                    if dato[0]=="fecha":
                        display.open_win("Fecha")
                        display.write_HMI("get_date","digit_clock","digit_clock1","")
                        fecha=1
                    if dato[0]=="atras_pre":
                        if config_value==2:
                            display.save_presiones(presiones)
                            config_value=0
                            time_buzz=(int(presiones[6])*60)*1000
                            timer_limit=(presiones[5]*60)*1000 #tiempo refuerzo
                            """#paro_bombas=(int(presiones[6])*60)*1000 #tiempo enc
                            #timer_out_bomb=(presiones[5]+int(presiones[6]))*2 #tiempo de seguridad de apagado de bombas
                            #timer_out_bomb=60 if timer_out_bomb>60 else timer_out_bomb
                            #timer_out_bomb=timer_out_bomb*60*1000"""
                            mod=1
                            for i in range(5):
                                display.write_HMI("set_text","label",dir_param[i],str(presiones[i])) if i!=2 else None
                            """#for i in range(3):
                            #    display.write_HMI("set_text","label",f"T_{i+1}","T.Stop "+str(int(paro_bombas/1000))+"s = 0s T.On")"""
                            cambio_motor=display.rect_cambio(cambio_motor,modos,display.obtener_menor_tiempo(hmi_time,mod,modos))
                            c_m=display.operacion(modos,cambio_motor,mod) #automatico,arranque,modo
                            cambio_motor=c_m[0]
                            mod_enviar=c_m[1]
                            ult_modos=modos
                        display.close_win("conf_presion")
                        ventanas=0
                if ventanas==2:
                    if dato[0]=="edit_sen":
                        display.open_win("user")
                        config_value=1
                    if config_value==1:
                        verf=display.verificar_user(dato,claves,0) 
                        if dato[0]=="cancelar":   
                            display.close_win("user")   
                            config_value=0
                    if dato[0]=="atras_sen":
                        if config_value==2:
                            display.save_sensores(sensores)
                            config_value=0
                        display.close_win("conf_sen")
                        ventanas=0
                if ventanas==3:
                    if dato[0]=="man_uni2" and man[1]==0:
                        sleep_ms(retardo)
                        info_485=display.data_485("030400100100",4,"M2")
                        man[1]=1
                        display.write_HMI("set_image","image","motor2",str(dir_mot_c[man[1]]))
                    elif dato[0]=="man_uni2" and man[1]==1:
                        sleep_ms(retardo)
                        info_485=display.data_485("030400100000",4,"M2")
                        man[1]=0
                        display.write_HMI("set_image","image","motor2",str(dir_mot_c[man[1]]))
                    if dato[0]=="man_uni1" and man[0]==0:
                        Motor1.value(1)
                        man[0]=1
                        display.write_HMI("set_image","image","motor1",str(dir_mot_c[man[0]]))
                    elif dato[0]=="man_uni1" and man[0]==1:
                        Motor1.value(0)
                        man[0]=0
                        display.write_HMI("set_image","image","motor1",str(dir_mot_c[man[0]]))
                    if borrar_time==1:
                        verf=display.verificar_user(dato,claves,0)
                        if dato[0]=="cancelar":   
                            display.close_win("user")   
                            borrar_time=0
                    if dato[0]=="atras_param":
                        display.close_win("param")
                        ventanas=0
                        man=[0,0]
                    for i in range(len(rst)):
                        if dato[0]==f"reset{i+1}":
                            display.open_win("confirmacion")
                            rst[i]=1
                    for i in range(len(rst)):
                        if dato[0]=="continuar" and rst[i]==1:
                            display.open_win("user")
                            borrar_time=1
                    display.close_win("confirmacion")  if dato[0]=="atras_reiniciar" else None
                if ventanas==4:
                    if dato[0]=="atras_hist":
                        display.close_win("Historial")
                        ventanas=0 
        
        if config_value==1:
            if verf==1 or verf==2: #credenciales correctas
                display.config_enable(dir_en_hmi[verf]) #habilitar conf_pre
                verf=0
                claves=["R","1123","SIIM","1296","",""]
                config_value=2
        if borrar_time==1:
             if verf==2: #credenciales correctas
                if rst[0]==1:
                        timing1[3]=((0,0,0,0,0,0),2,"00:00:00")
                        stu=display.save_time_unit("U1",1,timing1[3])
                if rst[1]==1:
                        timing2[3]=((0,0,0,0,0,0),2,"00:00:00")
                        stu=display.save_time_unit("U2",1,timing2[3])
                hmi_time=[timing1[3][2],timing2[3][2]]
                display.close_win("user")
                display.close_win("confirmacion")
                borrar_time=0
                verf=0
                rst=[0,0]
                claves=["R","1123","SIIM","1296","",""]

        if buzzer==1: #Alarma sonora 
            if ticks_diff(ticks_ms(),time_b)>1000:
                if estado==1:
                    if silencio==0:
                        #print("on")
                        sleep_ms(retardo)
                        buzz.value(1) #buzzer on
                    estado=0
                else:
                    estado=1
                time_b=ticks_ms()
            if ticks_diff(ticks_ms(),time_b2)>time_buzz:
                silencio=0

        #if ticks_diff(ticks_ms(),time_rs4851)>10000: #sin lecturas punto
        #    punto_rocio=3
        #if ticks_diff(ticks_ms(),time_rs4852)>10000: #sin lecturas co
        #    mono=11
        #    sec=0
        if ticks_diff(ticks_ms(),time_disp_ult)>time_disp:
            display.param_unidades(PIN,data_valor,hmi_time,ventanas,dat_rs,punto_rocio,mono,sec)
            if ventanas==2:
                sensores=display.edit_sensores(sensores,dato,adc_filtrado,data_valor,config_value)
                dato=[0,0,0]
            for i in range(len(data_valor)):
                data_valor[i]=int(((adc_filtrado[dir_adc[i]]-sensores[i*3])*sensores[(i*3)+2])/sensores[(i*3)+1])

            PIN1 = [io[n].value() for n in dir_pin] #lectura de pines controlador
            PIN=PIN1+PIN2
            modos=[PIN[2],PIN[6]]
            print("estado pin",PIN)
            
            t_paro=[PIN[3],PIN[7]] #0 alerta temp, 1 normal
            if pt[16]==1:
                for i in range(len(modos)):
                    modos[i]=1 if t_paro[i]==1 and modos[i]==1 else 0
            
            if ult_modos==modos:
                pass
            else:
                if START_UNI==1:
                    retar=0
                    if pt[7]==1:
                        alerta[13]=1 #retardo cambio de unidad
                    AR=1
                    cont_retar=0
                mod_env2=mod_enviar.replace(",1",",0")
                if "M1,1" in mod_env2:
                    Motor1.value(1)
                elif "M1,0" in mod_env2:
                    Motor1.value(0)
                if "M2,1" in mod_env2:
                    sleep_ms(retardo)
                    #display.send_485("030400100100") #motor 2 motor on
                    info_485=display.data_485("030400100100",4,"M2")
                elif "M2,0" in mod_env2:
                    sleep_ms(retardo)
                    info_485=display.data_485("030400100000",4,"M2")
                cambio_motor=display.rect_cambio(cambio_motor,modos,display.obtener_menor_tiempo(hmi_time,mod,modos))
                c_m=display.operacion(modos,cambio_motor,mod) #automatico,arranque,modo
                cambio_motor=c_m[0]
                mod_enviar=c_m[1]
                ult_modos=modos
            timings=[timing1,timing2]  
            for i,timing in enumerate(timings):  
                dir_state=[]
                if  timing[0]==1:
                    conta[i]=int(ticks_diff(ticks_ms(),timing[1])/1000)
                    if conta[i]!=conta_ult[i]:                
                        timing[3]=display.time_format(timing[3][0],h[i]+1)
                        h[i]=int(timing[3][1])
                        hmi_time[i]=timing[3][2]
                    conta_ult[i]=conta[i]
                
                if PIN[(i*4)+1]==1: # EM1==1 motor 1 activado 1 y 5
                    display.write_HMI("set_image","gif",f"estado{i+1}","en_uso")
                    if timing[0]==0: #EM1 contador unidad 1 activado
                        timing[0]=1
                        timing[1]=ticks_ms()
                        timer=ticks_ms()
                else:
                    if timing[0]==1:
                        stu=display.save_time_unit(f"U{i+1}",timing[2],timing[3])
                        save_time1=stu
                        timing[0]=0
                    if PIN[i*4]==0 and PIN[(i*4)+2]==1: #S1=0 Motor normal ON_M1==1 motor 1 activado automatico 0 y 4, 2 y 6 
                            if f"M{i+1}" in mod_enviar:
                                display.write_HMI("set_image","gif",f"estado{i+1}","en_esperav")
                            else:
                                display.write_HMI("set_image","gif",f"estado{i+1}","en_esperaa")
                    else:
                            display.write_HMI("set_image","gif",f"estado{i+1}","fuera")
            if data_valor[1]>(presiones[3]-(presiones[3]-pt[18])) and data_valor[1]<=presiones[3] and pt[14]==1: #presion 70 - 90, izquierda valor leido, derecha valor guardado 
                START_UNI=1
                #sleep_ms(retardo)
                #rs485_hum.send_data("3,ACT,1")
                tiempo_bombas=ticks_ms()
                tiempo_seguridad=ticks_ms()
            if data_valor[1]>=presiones[4]: #presion 30
                START_UNI=0
            if data_valor[1]>=presiones[4]+15: #presion 35
                START_UNI=0
                sleep_ms(retardo)
                #rs485_hum.send_data("3,ACT,0")
            if PIN[0]==1 and cambio_motor==1 and mod==1: #Sobrecarga unidad 1
                cambio_motor=2
            if PIN[4]==1 and cambio_motor==2 and mod==1: #Sobrecarga unidad 2
                cambio_motor=1   

            if START==0 and PIN[0]==1 and PIN[4]==1:
                sleep_ms(retardo)
                info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                Motor1.value(0) #motor 1 apagado
                for i,t in enumerate(timings): 
                    t[0] = 0
                    t[2] = 0 
                    display.write_HMI("set_image","gif",f"estado{i+1}","fuera")
            if START==1:
                if START_UNI==1:
                    verf1=1
                    if verf2==0:
                        timer=ticks_ms()
                        verf2=1
                    #print("contador:",contador,"arranque:",arranque, "mod_enviar",mod_enviar)
                    #sleep_ms(retardo)
                    #rs485_hum.send_data("3,"+mod_enviar)
                    if "M1,1" in mod_enviar:
                        Motor1.value(1)
                    elif "M1,0" in mod_enviar:
                        Motor1.value(0)
                    if "M2,1" in mod_enviar:
                        sleep_ms(retardo)
                        info_485=display.data_485("030400100100",4,"M2") #motor 2 motor on
                    elif "M2,0" in mod_enviar:
                        sleep_ms(retardo)
                        info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                    PIN1 = [io[n].value() for n in dir_pin] #lectura de pines controlador
                    PIN=PIN1+PIN2
                    cont_pub_estado=cont_pub_estado+1
                    print(cont_pub_estado)
                    if cont_pub_estado>3:
                        cont_pub_estado=0
                        print("estados pines",PIN)
                        timings=[timing1,timing2]  
                        for i,timing in enumerate(timings):
                            if init_time[i]==0 and PIN[(i*4)+1]==1: #EM1
                                if PIN[(i*4)+1]==1 and PIN[i*4]==0 and PIN[(i*4)+2]==1: #EM1, SOBRE, AUTO
                                    if init_time[i]==0:
                                        cont_enc_units[i]=cont_enc_units[i]+1
                                        timing[2]=1
                                        init_time[i]=1
                                        timer=ticks_ms()
                                elif cambio_motor==i+1:
                                    print(f"Unidad {i+1} no activado")
                                    init_arranque=0
                                    if pt[3]==1:
                                        alerta[i+6]=1 #unidad 1 no activado 9
                                    timing[2]=0
                                    init_time[i]=0
                                    if mod==1:
                                        cambio_motor=display.rect_cambio(cambio_motor,modos,display.obtener_menor_tiempo(hmi_time,mod,modos))
                                        c_m=display.operacion(modos,cambio_motor,mod) #automatico,arranque,modo
                                        cambio_motor=c_m[0]
                                        mod_enviar=c_m[1]
                                    sleep_ms(retardo)
                                    """if i==0:
                                        Motor1.value(0)
                                    else:
                                        sleep_ms(retardo)
                                        display.send_485("030400100000") #apagar motor 2"""
                                    #cambio_motor=2
                            else:
                                if f"M{i+1}" in mod_enviar and init_time[i]==0:
                                    print(f"Hey no activado M{i+1}")
                                    retar=0
                                    if pt[3]==1:
                                        alerta[i+6]=1 #retardos de unidades no activadas
                                    cont_retar=0
                                    mod_env2=mod_enviar.replace(",1",",0")
                                    if "M1,0" in mod_env2:
                                        Motor1.value(0)
                                    elif "M2,0" in mod_env2:
                                        sleep_ms(retardo)
                                        info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                                    cambio_p=1
                        if cambio_p==1:
                            mod_env2=mod_enviar.replace(",1",",0")
                            if "M1,0" in mod_env2:
                                Motor1.value(0)
                            elif "M2,0" in mod_env2:
                                sleep_ms(retardo)
                                info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                            cambio_motor=display.rect_cambio(cambio_motor,modos,display.obtener_menor_tiempo(hmi_time,mod,modos))
                            c_m=display.operacion(modos,cambio_motor,mod) #automatico,arranque,modo
                            cambio_motor=c_m[0]
                            mod_enviar=c_m[1]
                            cambio_p=0
                if START_UNI==0:
                    if verf1==1:
                        Motor1.value(0)
                        sleep_ms(retardo)
                        info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                        #sleep_ms(1000)
                        init_time=[0,0]
                        refuerzo=[0,0]
                        contador=0
                        init_arranque=0
                        cont_pub_estado=0
                        #print("data enviar",hmi_time,mod,type(hmi_time),type(mod))
                        if cont_enc_units[0]<3 and cont_enc_units[1]<3:
                            cambio_motor=display.rect_cambio(cambio_motor,modos,display.obtener_menor_tiempo(hmi_time,mod,modos))
                        else:
                            if cont_enc_units[0]>2 and cont_enc_units[1]>2:
                                cont_enc_units=[0,0]
                        c_m=display.operacion(modos,cambio_motor,mod) #automatico,arranque,modo
                        cambio_motor=c_m[0]
                        mod_enviar=c_m[1]
                        verf1=0
                    if verf2==1:
                        START_UNI=0
                        verf2=0
                #print("tiempos:",ticks_diff(ticks_ms(),timer),timer,timer_limit,mod_enviar)
                if ticks_diff(ticks_ms(),timer)>timer_limit and verf1==1 and START_UNI==1 and pt[13]==1:
                    if ref_cambio==cambio_motor:
                        pass
                    else:
                        ref_cambio=cambio_motor
                        refuerzo[cambio_motor-1]=1
                        alerta[5]=1 if refuerzo[0]==1 and pt[2]==1 else 0
                        alerta[4]=1 if refuerzo[1]==1 and pt[2]==1 else 0
                    c_m=display.operacion(modos,ref_cambio,1) #automatico,arranque,modo
                    #print("respaldo",c_m)
                    sleep_ms(retardo)
                    if "M1,1" in c_m[1]:
                        Motor1.value(1)
                    if "M2,1" in c_m[1]:
                        sleep_ms(retardo)
                        info_485=display.data_485("030400100100",4,"M2") #motor 2 motor on
                    verf2=0
                    timer=ticks_ms()
            alerta[3]=1 if PIN[4]==1 and pt[1]==1 else 0 #sobrecarga m2
            alerta[2]=1 if PIN[0]==1 and pt[1]==1 else 0 #sobrecarga m1
            alerta[10]=1 if data_valor[1]<presiones[2] and pt[5]==1 else 0 #presion_tanque baja
            #print(alerta,data_valor,pt[5],presiones[2])
            alerta[11]=1 if data_valor[1]>=int(presiones[4]+15) and pt[5]==1 else 0 #presion_tanque alta
            alerta[8]=1 if data_valor[0]<=presiones[0] and pt[4]==1 else 0 #presion_salida baja
            alerta[9]=1 if data_valor[0]>=presiones[1] and pt[4]==1 else 0 #presion_salida alta
            alerta[0]=1 if PIN[3]==0 and pt[0]==1 else 0 #temp alta 1
            alerta[1]=1 if PIN[7]==0 and pt[0]==1 else 0 #temp alta 1
            alerta[14]=1 if punto_rocio>pt[22] and pt[8]==1 else 0
            alerta[15]=1 if mono>pt[23] and pt[9]==1 else 0
            #alerta[21]=0 if sec==0 else 0 #alerta secadores apagados
            #AC=1 if (alerta[0]==1 or alerta[1]==1 or alerta[2]==1) else 0
            AT=1 if (alerta[0]==1 or alerta[1]==1) else 0
            #AH=1 if (alerta[8]==1 or alerta[9]==1) else 0
            if (refuerzo[0]==1 or refuerzo[1]==1):
                AR=1
            
            #Guardar historial de alertas
            for i in range(0,len(alerta)):
                if alerta[i]==1 and alerta_hist[i]==0 and pt[15]==1:
                    alerta_hist[i]=1
                    print("alerta detectada...................")
                    try:
                        date=display.date()
                        display.guardar_registro(str(date[1])+"  "+dir_alert[i])
                    except:
                        print("NONE")
                if alerta[i]==0 and alerta_hist[i]==1 and pt[15]==1:
                    alerta_hist[i]=0
                    
            if PIN[1]==1 and PIN[5]==1 and retar==0:
                retar=1
                if pt[6]==1:
                    alerta[12]=1 #retardo ambas unidades
                AR=1
                cont_retar=0
            if retar==1 and PIN[1]==0 and PIN[5]==0:
                retar=0
            #print("alertas",alerta,alerta2)
            if any(x == 1 for x in alerta) or PIN[0]==1 or PIN[4]==1:
                AG=1
                if alerta!=alerta2:
                    if pt[12]==1:
                        buzzer=1
                    silencio=0
                    time_b=ticks_ms()
                    text_alert="" #en el arranque iniciar los dos motores
                    rest=1
                    for i in range(0,len(alerta)):
                        if alerta[i]==1:
                            text_alert=text_alert+dir_alert[i]+":"
                    display.set_visible("barra","true")
                    if alerta[10]==1 or alerta[11]==1:
                        display.set_color("tanque_psi","text_color",0x96,0x0,0x0,0xff) #color widget
                    else:
                        display.set_color("tanque_psi","text_color",0x44,0x44,0x44,0xff) #color widget
                    if alerta[8]==1 or alerta[9]==1:
                        display.set_color("hosp_psi","text_color",0x96,0x0,0x0,0xff) #color widget
                    else:
                        display.set_color("hosp_psi","text_color",0x44,0x44,0x44,0xff) #color widget
                    for i in range(0,len(alerta)):
                        alerta2[i]=alerta[i]
                    display.write_HMI("set_text","hscroll_label","mensaje",str(text_alert))
                    display.write_HMI("set_image","gif","estatus","alerta")
            if all(x == 0 for x in alerta) and PIN[0]==0 and PIN[4]==0:
                AG=0
                buzzer=0
                silencio=0
                sleep_ms(retardo)
                buzz.value(0) #buzzer off
                if rest==1:
                    display.set_visible("barra","false")
                    display.write_HMI("set_image","gif","estatus","normal")
                    display.write_HMI("set_text","hscroll_label","mensaje","")
                    display.set_color("hosp_psi","text_color",0x44,0x44,0x44,0xff) #color widget
                    display.set_color("tanque_psi","text_color",0x44,0x44,0x44,0xff) #color widget
                    rest=0
                alerta2=[0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0]
            time_disp_ult=ticks_ms()
            ciclo=ciclo+1
            if ciclo>=10 and ventanas==0:
                dir_pro=["hosp_bar","tanque_bar"]
                dir_roc=["rocio_bar","mono_bar"]
                dir_roc1=[-60,2,0,10]
                dir_bar=[punto_rocio,mono]
                #print("data_valor",data_valor)
                for i in range(2):
                    p_diff=data_valor[i]-presiones[i*3]
                    p_diff=0 if p_diff<=0 else p_diff
                    p_diff=((p_diff*100)/(presiones[(i*3)+1]-presiones[i*3]))
                    p_diff=0 if p_diff<=0 else p_diff
                    p_diff=100 if p_diff>=100 else p_diff
                    display.write_HMI("set_value","progress_bar",dir_pro[i],str(int(p_diff)))
                for i in range(2):
                    p_diff=dir_bar[i]-(dir_roc1[i*2])
                    p_diff=0 if p_diff<=0 else p_diff
                    p_diff=((p_diff*100)/(dir_roc1[(i*2)+1]-(dir_roc1[i*2])))
                    p_diff=0 if p_diff<=0 else p_diff
                    p_diff=100 if p_diff>=100 else p_diff
                    display.write_HMI("set_value","progress_bar",dir_roc[i],str(int(p_diff)))
                    #print("bar:",int(p_diff))
                ciclo=0
run()