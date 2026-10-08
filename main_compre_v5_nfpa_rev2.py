def run(): 
    from machine import Pin
    from time import sleep_ms, ticks_ms, ticks_diff
    import configuracion as display
    import math
    import mod485
    import app

    # ======================= Config =======================
    POLL_PEND_MS     = 1000     # cada cuanto preguntamos si hay pendientes
    READ_TIMEOUT_MS  = 300      # timeout para leer la respuesta a PEND_READ
    POLL_TIMEOUT_MS  = 200      # timeout para leer la respuesta a PEND_COUNT

    # ======================= Loop principal =======================
    lastPollPending = 0


    MAX_MOTORS = 6
    MAX_SENS = 3

    '''
    INIT_DATA
    '''
    n_units = 2             # Número de unidades en el compresor
    typ_secadores = 0       # Tipo de secadores(0-Disecantes, 1-Refrigerativos)
    n_sens_per_unit = 2     # Numero de sensores de temperatura por cada unidad
    typ_sens = 0            # Tipo de sensores de temperatura (0-Digital, 1-Analogos)

    ventanas=0 #0 normal 1 presiones 2 sensores 3 unidades 4 historial
    config_value=0
    config_sen=0
    silencio = 1
    borrar_time=0
    fecha=0
    pt=display.leer_parametros()
    sec=display.leer_secadores()
    module=display.leer_hex()
    print("param:",pt)
    claves=["R","1123","SIIM","1296","",""]
    clav_m=["RSIIM","11231296","","","",""]
    verf=0
    Fecha=""
    retardo=pt[19]
    rst=[0,0]
    pines = {"S1": 33, "EM1": 25, "AUTO": 4, "TEMP1": 32, "TEMP2": 35} 
    dir_pin = ["S1", "EM1", "AUTO", "TEMP1", "TEMP2"]
    dir_en_hmi=["","presiones","sensores"]
    dir_alert=["Falla termica scroll A","Falla termica scroll B",
                "Unidad 1 en sobrecarga","Unidad 2 en sobrecarga",
                "Respaldo Unidad 1","Respaldo Unidad 2",
                "Retardo, Unidad 1 no activado","Retardo, Unidad 2 no activado",
                "Presion de salida baja","Presion de salida alta","Presion de tanque baja","Presion de tanque alta",
                "Retardo, unidades encendidas","Retardo, Cambio de unidad","Punto de rocio alto","Alerta de CO",
                "Punto de Rocio sin conexion","Modulo PR y CO sin conexion","Modulo M2 sin conexion","Modulo alarmas sin conexion",
                "Mem_Ext sin conexion","Mem_SD no conectada","Modulo WiFi fallo","Falla termica scroll A","Falla termica scroll B"] #25
    alpha=float(pt[16])#0.01#0.012
    adc_presion=[0,0]
    adc_filtrado=[0,0]
    alerta=     [0,0,0,0,0 ,0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0] #23 alertas
    alerta2=    [0,0,0,0,0 ,0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0] #23 alertas
    alerta_hist=[0,0,0,0,0 ,0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0] #23 alertas
    PIN1=[0,0,0,0,0]
    PIN2=[0,0,0,0,0]
    #mod_enviar="M1,0,M2,0"
    io = {nombre: Pin(pin, Pin.IN, Pin.PULL_DOWN) for nombre, pin in pines.items()}
    PIN1 = [io[n].value() for n in dir_pin] #lectura de pines controlador
    buzz=Pin(22,Pin.OUT)
    Motor1=Pin(23,Pin.OUT)
    presiones=display.leer_presiones()
    sensores=display.leer_sensores()
    time_disp=pt[18]
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
    modos=[PIN[2],PIN[7]]
    t_paro=[PIN[3],PIN[4],PIN[8],PIN[9]]
    ult_modos=modos
    cambio_motor=1
    #menor_uni=display.obtener_menor_tiempo(tiempos=hmi_time)
    print("cambio_motor1",cambio_motor)
    #print("tiempos unidades:",hmi_time)
    #print("unidad menor tiempo:",menor_uni)
    
    sleep_ms(5000)
    bloque=Pin(36,Pin.IN)
    bloqueo=bloque.value()
    if bloqueo==0:
        display.open_win("alerta_giro")
        buzz.value(1) #buzzer on
    display.close_win("alerta_giro")
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
    init_sec=module[4] #"02030000" 
    init_mot=module[1] #"03030000" 
    Mot2=[0,0] #motor, salida24v
    dir_modulo_485=[module[0],init_sec,init_mot,module[5]]
    name_modulo=["PR","SC","M2","AL"]
    modo_master=[0,0,0,0]
    mod_ing=0
    verfm=0
    info_485=[0,0]
    config_mod=1
    Sec_1=sec[0]
    Sec_2=sec[1]
    man=[0,0]
    paro_motor=0
    cambio_secadores=0
    est_uni=[0,0] #estado de unidades = unidad 1, unidad 2
    est_pre=[0,0] #estado de presiones = hosp,tanque
    time_unit=[0,0] #tiempo de unidades en segundos
    
    MAX_MOTORS = 6
    MAX_SENS = 3
    data_temp_tl = 2

    temperaturas_monitoreo = [[[0 for _ in range(data_temp_tl)] for _ in range(MAX_SENS)] for _ in range(MAX_MOTORS)]
    #temperaturas_monitoreo[0][1][1] = estado  #### Ejemplo para asignar el estado del sensor 2 de la unidad 1 (reemplace 'estado' por el valor real)

    umbral_temperaturas_alta = [[0 for _ in range(MAX_SENS)] for _ in range(MAX_MOTORS)]
    # umbral_temperaturas_alta[1][2] = temp_alta_sens3_u2   #### Ejemplo para asignar el limite en temperatura alta para el sensor 3 de la unidad 2 (reemplace 'temp_alta_sens3_u2' por el valor real)

    adc_sens_temperatura = [[[0 for _ in range(3)] for _ in range(MAX_SENS)] for _ in range(MAX_MOTORS)]
    # adc_sens_temperatura[2][1][1] = adc_max_sens2_u3 #### Ejemplo para asignar el valor adc maximo del sensor 2 de la unidad 3 (reemplace 'adc_max_sens2_u3' por el valor real)
    
    # =========== ESTADOS DE CONEXION MQTT Y WIFI ============
    lastGetConnSt = 0
    timeIntervalGetConnSt = 5000
    wifi_st = 3     # - WiFi: 0 -> Conectado  |  1 -> Desconectado  |  3 -> Apagado       |  2 -> AP o Punto de Acceso (¡No se usa aquí!)
    mqtt_st = 3     # - MQTT: 0 -> Conectado  |  1 -> Desconectado  |  2 -> Reconectando  |  3 -> Apagado
    dir_wifi=["wifi_ok","wifi_no","wifi_off","wifi_off"]
    dir_mqtt=["data_ok","data_no","data_rec","data_off"]
    dir_inf=["ok","no","rec","off"]
    #time_unit=display.obtener_segundos(hmi_time)
    #print(time_unit,hmi_time)
    #sleep_ms(5000)



    # ===================== Polling ========================
    def _send_cmd_byte(cmd):
        """Manda una trama de comando simple con el byte cmd"""
        app.send_simple_command(cmd)

    def _read_frame(timeout_ms):
        t0 = ticks_ms()
        while ticks_diff(ticks_ms(), t0) < timeout_ms:
            if mod485.rs485_available():
                pkt = mod485.read_conf()
                if pkt and pkt[0] == 0x7E:
                    return pkt
            sleep_ms(2)
        return None

    def wait_response(timeout_ms):
        """Espera una trama completa por RS485. Devuelve bytes o None."""
        t0 = ticks_ms()
        while ticks_diff(ticks_ms(), t0) < timeout_ms:
            if mod485.rs485_available():
                data = mod485.read_conf()
                if data and len(data) >= 1 and data[0] == 0x7E:
                    return data
            sleep_ms(2)
        return None

    def poll_pending():
        """
        1. Pregunta cuántos pendientes hay.
        2. Lee uno a uno (mayor prioridad primero) y los procesa.
        """
        # --- 1) PEND_COUNT ---
        app.send_simple_command(app.CMD_PEND_COUNT)
        data = wait_response(POLL_TIMEOUT_MS)
        if data is None:
            return
        resp = app.process_command(data)
        if not isinstance(resp, dict) or resp.get('type') != 'pend_count':
            return
        n = int(resp.get('count', 0))
        if n == 0:
            return

        print(f"[PEND] {n} mensajes pendientes")

        # --- 2) PEND_READ x N ---
        for _ in range(n):
            app.send_simple_command(app.CMD_PEND_READ)
            data = wait_response(READ_TIMEOUT_MS)
            if data is None:
                print("[PEND] timeout leyendo, abortando")
                break
            comando = app.process_command(data)
            if not isinstance(comando, dict):
                continue
            if comando.get('type') == 'pend_empty':
                # El esclavo no tenía nada (por ejemplo TTL expiró entre COUNT y READ)
                break
            handle_message(comando)

    # ============== Despacho ====================
    def handle_message(comando):
        nonlocal silencio, time_b2, wifi_st, mqtt_st, AR, cont_retar

        tipo = comando.get('type')
        # ===== Ejecutar comando de buzzer ====
        if tipo == 'buzzer':
            '''
            Codigo que silencia al buzzer
            '''
            print("#############################################################################")
            app.send_ack_nack(True)
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
        elif tipo == 'red_st':
            '''
            Actualizar estado de comunicacion en el HMI donde:
                - WiFi: 0 -> Conectado  |  1 -> Desconectado  |  3 -> Apagado       |  2 -> AP o Punto de Acceso (¡No se usa aquí!)
                - MQTT: 0 -> Conectado  |  1 -> Desconectado  |  2 -> Reconectando  |  3 -> Apagado
            '''
            wifi_st, mqtt_st = ( comando['wifi'], comando['mqtt'] )
        elif tipo == 'get_data':
            '''
            Colocar código que envia datos de telemetria
            '''
            estados_unidad = [0]*MAX_MOTORS
            tiempos_work = [0]*MAX_MOTORS
            #print(time_unit)
            for i in range(n_units):
                estados_unidad[i] = est_uni[i]
                tiempos_work[i] = time_unit[i]

            secadores_estado = (sec[1] << 1) | sec[0]
            
            payload = app.build_comp_frame(
                p_out=data_valor[0],
                p_out_st=est_pre[0],
                p_tank=data_valor[1],
                p_tank_st=est_pre[1],
                p_rocio=int(punto_rocio),
                p_rocio_st=alerta[14],
                co_ppm=mono,
                co_ppm_st=alerta[15],
                unidad_st=estados_unidad,
                unidad_tmp=app.flatten(temperaturas_monitoreo),
                unidad_trb=tiempos_work,
                secador_st=secadores_estado
            )
            packet = app.build_packet(payload=payload)
            mod485.send_conf(packet)
        #### ==== Enviar Configuraciones ====
        elif tipo == 'get_config_init':
            '''
            Colocar codigo para enviar la configuracion de init
            '''
            payload = app.build_comp_init(
                n_unidades=n_units,
                typ_secadores=typ_secadores,
                typ_temp_sens=typ_sens,
                n_temp_sens=n_sens_per_unit
            )
            packet = app.build_packet(payload=payload)
            mod485.send_conf(packet)
        elif tipo == 'get_config_th':
            '''
            Colocar codigo para enviar la configuracion de umbrales
            '''
            temps_hig = app.flatten(umbral_temperaturas_alta)
            payload = app.build_comp_th(
                th_p_out=[presiones[0],presiones[1]],
                th_p_tank=[presiones[2], presiones[3], presiones[4]],
                time_ref=presiones[5],
                time_sil=presiones[6],
                temp_high=temps_hig
            )
            packet = app.build_packet(payload=payload)
            mod485.send_conf(packet)
        elif tipo == 'get_config_sensors':
            '''
            Colocar codigo para enviar la configuracion de sensores
            '''
            sensor_temp_adc = app.flatten(adc_sens_temperatura)
            payload = app.build_comp_sens(
                sensor_out= [sensores[0], sensores[1], sensores[2]],
                sensor_tank=[sensores[3], sensores[4], sensores[5]],
                sensor_temp=sensor_temp_adc
            )
            packet = app.build_packet(payload=payload)
            mod485.send_conf(packet)
        elif tipo == 'get_config_alerts':
            '''
            Colocar codigo para enviar la configuracion de alertas
            '''
            sw_alerts = app.pack_sw_bits(pt[0],pt[1],pt[2],pt[3],pt[4],pt[5],pt[6],pt[7],pt[8],pt[9],pt[10],pt[11],pt[12],pt[13],pt[14],pt[15])
            alpha_i = int(round(pt[16]*10000))
            payload = app.build_comp_alerts(
                sw=sw_alerts,
                alpha=alpha_i,
                niv_seg=pt[17],
                act_HMI=pt[18],
                dat_mod=pt[19], 
                pet_mod=pt[20],
                pt_max=pt[21],
                co_max=pt[22],
                comp_pt=[pt[23], pt[24]]
            )
            packet = app.build_packet(payload=payload)
            mod485.send_conf(packet)
        #### ==== Guardar Configuraciones ====
        elif tipo == 'cnf_th':
            '''
            Colocar codigo para guardar la configuracion de umbrales
            '''
            umbral_temperaturas_alta = comando["temp_high"]
            presiones[0], presiones[1]               = (comando["th_p_out"][0], comando["th_p_out"][1])
            presiones[2], presiones[3], presiones[4] = (comando["th_p_tank"][0], comando["th_p_tank"][1], comando["th_p_tank"][2])
            presiones[5] = comando["time_ref"]
            presiones[6] = comando["time_sil"]

            ## TODO: Implementar funcion para guardar parametros
            #app.send_ack_nack(True)
            display.save_presiones(presiones)
        elif tipo == 'cnf_sens':
            '''
            Colocar codigo para guardar la configuracion de sensores
            '''
            presiones[0], presiones[1], presiones[2] = (comando["sensor_out"][0], comando["sensor_out"][1], comando["sensor_out"][2]) 
            presiones[3], presiones[4], presiones[5] = (comando["sensor_tank"][0], comando["sensor_tank"][1], comando["sensor_tank"][2])
            adc_sens_temperatura = comando["sensor_temp"]
            ## TODO: Implementar funcion para guardar parametros
            
            #app.send_ack_nack(True)
            display.save_sensores(sensores)
        elif tipo == 'cnf_alerts':
            '''
            Colocar codigo para guardar la configuracion de alertas
            '''
            index_pt = 0
            for _ in range(16):
                pt[index_pt] = comando["sw_bits"][index_pt]
                index_pt += 1
            pt[index_pt] = comando["alpha"] / 10000.0
            index_pt += 1
            pt[index_pt] = comando["niv_seg"]
            index_pt += 1
            pt[index_pt] = comando["act_HMI"]
            index_pt += 1
            pt[index_pt] = comando["dat_mod"]
            index_pt += 1
            pt[index_pt] = comando["pet_mod"]
            index_pt += 1
            pt[index_pt] = comando["pt_max"]
            index_pt += 1
            pt[index_pt] = comando["co_max"]
            index_pt += 1
            pt[index_pt] = comando["comp_pt"][0]
            index_pt += 1
            pt[index_pt] = comando["comp_pt"][1]
            
            #nuevos_valores_alerts = [*comando["sw_bits"], comando["alpha"], comando["niv_seg"], comando["act_HMI"], comando["dat_mod"], comando["pet_mod"], comando["pt_max"], comando["co_max"], *comando["comp_pt"]]
            #pt[:] = nuevos_valores_alerts

            ## TODO: Implementar funcion de guardado/actualizacion de pt
            #app.send_ack_nack(True)
            #cambiar alpha a float de 4 decimales
            display.guardar_par(pt)
        #### ==== Notificar errores en la ejecución de acciones ====
        elif tipo == 'warning' or tipo == 'error':
            print(f"[{tipo.upper()}] - {comando.get('msg')}")
            app.send_ack_nack(False)
        else:
            print(f"Tipo de comando no manejado: {comando}")
            app.send_ack_nack(False)



    while True:

        '''
        Comunicacion con el modulo mqtt
        '''
        # ======== Solicita el estado de red del dispositivo mqtt =======
        if ticks_diff(ticks_ms(), lastGetConnSt) > timeIntervalGetConnSt:
            lastGetConnSt = ticks_ms()
            app.send_simple_command('red')


        # ------------ Polling de pendientes -------------
        if ticks_diff(ticks_ms(), lastPollPending) > POLL_PEND_MS:
            lastPollPending = ticks_ms()
            print("Haciendo polling....")
            try:
                poll_pending()
            except Exception as e:
                print("Error en poll_pending: ",e)

        ######### ===== Cuando se guarden nuevas configuraciones desde el HMI se debe enviar la nueva configuracion tal como se hace en los casos donde tipo == 'get_config_...' para que se apliquen tanto en el dispositivo como en la nube

            
            


        dir_modulo_485[1]=init_sec+f'{Sec_1 & 0XFFFF:02x}'+f'{Sec_2 & 0XFFFF:02x}'
        dir_modulo_485[2]=init_mot+f'{Mot2[0] & 0XFFFF:02x}'+f'{Mot2[1] & 0XFFFF:02x}'
        for i in range(0,2):
            adc_presion[i]=display.adc(i)
            adc_filtrado[i]=(alpha*adc_presion[i])+((1-alpha)*adc_filtrado[i])
        PIN1 = [io[n].value() for n in dir_pin] #lectura de pines controlador
        PIN=PIN1+PIN2
        if ticks_diff(ticks_ms(),time_peticion)>pt[20]:
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
            info_485=display.data_485(dat,dir_e,m_name,module)
            #print("data",pt[9])
            for i in range(len(name_modulo)):
                if m_name==name_modulo[i] and info_485[0]==0 and pt[9]==1:
                    alerta[i+16]=1
            if info_485[0]==1: #punto de rocio y co
                #punto_rocio=info_485[1]
                b1=243.04
                a1=17.625
                #print(info_485)
                H=info_485[2]-pt[24]
                T=info_485[3]-pt[23]
                try:
                    punto_rocio=int(((b1*((math.log(H/100))+((a1*T)/(b1+T))))/(a1-math.log(H/100)-(a1*(T/(b1+T)))))*10)/10
                except:
                    pass
                
                print("val_punto",punto_rocio,info_485)
                #punto_rocio=info_485[1]
                alerta[16]=0
            if info_485[0]==2: #secadores
                #PR=info_485[1] #dato de PR enviado y recibido
                mono=info_485[2] #dato de co
                mono=0 if mono<0 else mono
                sec=[info_485[3],info_485[4]] #secador 1 y secador 2
                alerta[17]=0
                #print(info_485)
            if info_485[0]==3: #tarjeta motor
                #print("tarjeta motor:",info_485)
                PIN2[1]=info_485[3] #contactor motor 2
                PIN2[0]=info_485[2] #sobrecarga motor 2
                PIN2[4]=info_485[5] #temperatura motor 2
                PIN2[2]=info_485[4] #automatico motor 2
                PIN2[3]=info_485[1] #entrada dig mot2 temp2
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
                
                for i in range(len(sec)):
                    if dato[0]==f"sec{i+1}" and sec[i]==0:
                        sec[i]=1
                        display.write_HMI("set_image","image",f"sec_{i+1}",str(sec_c[sec[i]]))
                        display.guardar_secadores(sec)
                        cambio_secadores=1
                    elif dato[0]==f"sec{i+1}" and sec[i]==1:
                        sec[i]=0
                        display.write_HMI("set_image","image",f"sec_{i+1}",str(sec_c[sec[i]]))
                        display.guardar_secadores(sec)
                        cambio_secadores=1
                if cambio_secadores==1:
                    Sec_1=sec[0]
                    Sec_2=sec[1]
                    cambio_secadores=0
                    
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
                    display.menu_ing(pt,module)
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
                        #sleep_ms(retardo)
                        Mot2[0]=1 #activar motor
                        #info_485=display.data_485("030400100100",4,"M2") #"030300000005"
                        man[1]=1
                        display.write_HMI("set_image","image","motor2",str(dir_mot_c[man[1]]))
                    elif dato[0]=="man_uni2" and man[1]==1:
                        #sleep_ms(retardo)
                        Mot2[0]=0 #desactivar motor
                        #info_485=display.data_485("030400100000",4,"M2")
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
                        Mot2=[0,0]
                        if man[0]==1:
                            Motor1.value(0)
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
            display.write_HMI("set_image","image","wifi",dir_wifi[wifi_st])
            display.write_HMI("set_image","image","mqtt",dir_mqtt[mqtt_st])
            display.write_HMI("set_text","label","info_wifi","Mqtt:"+dir_inf[mqtt_st]+" Wifi:"+dir_inf[wifi_st])
            display.param_unidades(PIN,data_valor,hmi_time,ventanas,dat_rs,punto_rocio,mono,sec)
            if ventanas==2:
                sensores=display.edit_sensores(sensores,dato,adc_filtrado,data_valor,config_value)
                dato=[0,0,0]
            for i in range(len(data_valor)):
                data_valor[i]=int(((adc_filtrado[dir_adc[i]]-sensores[i*3])*sensores[(i*3)+2])/sensores[(i*3)+1])

            PIN1 = [io[n].value() for n in dir_pin] #lectura de pines controlador
            PIN=PIN1+PIN2
            modos=[PIN[2],PIN[7]] 
            #print("estado pin",PIN)
            
            t_paro=[PIN[3],PIN[4],PIN[8],PIN[9]] #0 alerta temp, 1 normal {"S1": 33, "EM1": 25, "AUTO": 4, "TEMP1": 32, "TEMP2": 35} 
            if pt[15]==1:
                for i in range(len(modos)):
                    modos[i]=1 if t_paro[i*2]==1 and t_paro[(i*2)+1]==1 and modos[i]==1 else 0
            else:
                t_paro=[1,1,1,1]
            if ult_modos==modos:
                pass
            else:
                if START_UNI==1:
                    retar=0
                    if pt[6]==1:
                        alerta[13]=1 #retardo cambio de unidad
                    AR=1
                    cont_retar=0
                mod_env2=mod_enviar.replace(",1",",0")
                if "M1,1" in mod_env2:
                    Motor1.value(1)
                elif "M1,0" in mod_env2:
                    Motor1.value(0)
                if "M2,1" in mod_env2:
                    #sleep_ms(retardo)
                    #display.send_485("030400100100") #motor 2 motor on
                    #info_485=display.data_485("030400100100",4,"M2")
                    Mot2[0]=1 #activar motor
                elif "M2,0" in mod_env2:
                    #sleep_ms(retardo)
                    #info_485=display.data_485("030400100000",4,"M2")
                    Mot2[0]=0 #desactivar motor
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
                if PIN[(i*5)+1]==1 and t_paro[i*2]==1 and t_paro[(i*2)+1]==1: # EM1==1 motor 1 activado 1 y 5 {"S1": 33, "EM1": 25, "AUTO": 4, "TEMP1": 32, "TEMP2": 35} 
                    display.write_HMI("set_image","gif",f"estado{i+1}","en_uso")
                    est_uni[i]=1
                    if timing[0]==0: #EM1 contador unidad 1 activado
                        timing[0]=1
                        timing[1]=ticks_ms()
                        timer=ticks_ms()
                else:
                    if timing[0]==1:
                        stu=display.save_time_unit(f"U{i+1}",timing[2],timing[3])
                        save_time1=stu
                        timing[0]=0
                    if PIN[i*5]==0 and PIN[(i*5)+2]==1 and t_paro[i*2]==1 and t_paro[(i*2)+1]==1: #S1=0 Motor normal ON_M1==1 motor 1 activado automatico 0 y 4, 2 y 6 
                            if f"M{i+1}" in mod_enviar:
                                display.write_HMI("set_image","gif",f"estado{i+1}","en_esperav")
                                est_uni[i]=3
                            else:
                                display.write_HMI("set_image","gif",f"estado{i+1}","en_esperaa")
                                est_uni[i]=2
                    else:
                            display.write_HMI("set_image","gif",f"estado{i+1}","fuera")
                            est_uni[i]=0
            if data_valor[1]>(presiones[3]-(presiones[3]-pt[17])) and data_valor[1]<=presiones[3] and pt[13]==1: #presion 70 - 90, izquierda valor leido, derecha valor guardado 
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
                mod_enviar=mod_enviar.replace("M1","M2")
                #print("m1:",mod_enviar)
            if PIN[5]==1 and cambio_motor==2 and mod==1: #Sobrecarga unidad 2
                cambio_motor=1
                mod_enviar=mod_enviar.replace("M2","M1")
                #print("m2:",mod_enviar)
            if START==0 and PIN[0]==1 and PIN[5]==1:
                #sleep_ms(retardo)
                #info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                Mot2[0]=0 #desactivar motor
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
                        #sleep_ms(retardo)
                        Mot2[0]=1 #activar motor
                        #info_485=display.data_485("030400100100",4,"M2") #motor 2 motor on
                    elif "M2,0" in mod_enviar:
                        #sleep_ms(retardo)
                        Mot2[0]=0 #desactivar motor
                        #info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                    PIN1 = [io[n].value() for n in dir_pin] #lectura de pines controlador
                    PIN=PIN1+PIN2
                    cont_pub_estado=cont_pub_estado+1
                    #print(cont_pub_estado)
                    if cont_pub_estado>8:
                        cont_pub_estado=0
                        print("estados pines",PIN)
                        timings=[timing1,timing2]  
                        for i,timing in enumerate(timings):
                            if init_time[i]==0 and PIN[(i*5)+1]==1: #EM1
                                if PIN[(i*5)+1]==1 and PIN[i*5]==0 and PIN[(i*5)+2]==1: #EM1, SOBRE, AUTO
                                    if init_time[i]==0:
                                        cont_enc_units[i]=cont_enc_units[i]+1
                                        timing[2]=1
                                        init_time[i]=1
                                        timer=ticks_ms()
                                elif cambio_motor==i+1:
                                    print(f"Unidad {i+1} no activado")
                                    init_arranque=0
                                    if pt[2]==1:
                                        alerta[i+6]=1 #unidad 1 no activado 9
                                    timing[2]=0
                                    init_time[i]=0
                                    if mod==1:
                                        #cambio_motor=display.rect_cambio(cambio_motor,modos,display.obtener_menor_tiempo(hmi_time,mod,modos))
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
                                    if pt[2]==1:
                                        alerta[i+6]=1 #retardos de unidades no activadas
                                    cont_retar=0
                                    mod_env2=mod_enviar.replace(",1",",0")
                                    if "M1,0" in mod_env2:
                                        Motor1.value(0)
                                    elif "M2,0" in mod_env2:
                                        #sleep_ms(retardo)
                                        Mot2[0]=0 #desactivar motor
                                        #info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                                    cambio_p=1
                                    print("cambio motor:",cambio_motor)
                        if cambio_p==1:
                            mod_env2=mod_enviar.replace(",1",",0")
                            if "M1,0" in mod_env2:
                                Motor1.value(0)
                            elif "M2,0" in mod_env2:
                                #sleep_ms(retardo)
                                Mot2[0]=0 #activar motor
                                #info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                            #cambio_motor=display.rect_cambio(cambio_motor,modos,display.obtener_menor_tiempo(hmi_time,mod,modos))
                            c_m=display.operacion(modos,cambio_motor,mod) #automatico,arranque,modo
                            cambio_motor=c_m[0]
                            mod_enviar=c_m[1]
                            cambio_p=0
                            print("cambio_p",cambio_motor,c_m)
                if START_UNI==0:
                    if verf1==1:
                        Motor1.value(0)
                        #sleep_ms(retardo)
                        #info_485=display.data_485("030400100000",4,"M2") #motor 2 motor off
                        Mot2[0]=0 #desactivar motor
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
                if ticks_diff(ticks_ms(),timer)>timer_limit and verf1==1 and START_UNI==1 and pt[12]==1:
                    if ref_cambio==cambio_motor:
                        pass
                    else:
                        ref_cambio=cambio_motor
                        refuerzo[cambio_motor-1]=1
                        alerta[5]=1 if refuerzo[0]==1 else 0
                        alerta[4]=1 if refuerzo[1]==1 else 0
                    c_m=display.operacion(modos,ref_cambio,1) #automatico,arranque,modo
                    #print("respaldo",c_m)
                    sleep_ms(retardo)
                    if "M1,1" in c_m[1]:
                        Motor1.value(1)
                    if "M2,1" in c_m[1]:
                        #sleep_ms(retardo)
                        #info_485=display.data_485("030400100100",4,"M2") #motor 2 motor on
                        Mot2[0]=1 #ctivar motor
                    verf2=0
                    timer=ticks_ms()
            alerta[3]=1 if PIN[5]==1 and pt[1]==1 else 0 #sobrecarga m2
            alerta[2]=1 if PIN[0]==1 and pt[1]==1 else 0 #sobrecarga m1
            est_uni[0]=4 if alerta[2]==1 else est_uni[0]
            est_uni[1]=4 if alerta[3]==1 else est_uni[1]
            alerta[10]=1 if data_valor[1]<presiones[2] and pt[4]==1 else 0 #presion_tanque baja
            #print(alerta,data_valor,pt[4],presiones[2])
            alerta[11]=1 if data_valor[1]>=int(presiones[4]+15) and pt[4]==1 else 0 #presion_tanque alta
            alerta[8]=1 if data_valor[0]<=presiones[0] and pt[3]==1 else 0 #presion_salida baja
            alerta[9]=1 if data_valor[0]>=presiones[1] and pt[3]==1 else 0 #presion_salida alta
            alerta[0]=1 if PIN[3]==0 and pt[0]==1 else 0 #temp alta 1
            alerta[1]=1 if PIN[4]==0 and pt[0]==1 else 0 #temp alta 1
            alerta[23]=1 if PIN[8]==0 and pt[0]==1 else 0 #temp alta 2 
            alerta[24]=1 if PIN[9]==0 and pt[0]==1 else 0 #temp alta 2
            alerta[14]=1 if punto_rocio>pt[21] and pt[7]==1 else 0
            alerta[15]=1 if mono>pt[22] and pt[8]==1 else 0
            
            temperaturas_monitoreo[0][0][1] = 2 if alerta[0]  == 0 else 0
            temperaturas_monitoreo[0][1][1] = 2 if alerta[1]  == 0 else 0
            temperaturas_monitoreo[1][0][1] = 2 if alerta[23] == 0 else 0
            temperaturas_monitoreo[1][1][1] = 2 if alerta[24] == 0 else 0
            if alerta[8]==1:
                est_pre[0]=1
            if alerta[9]==1:
                est_pre[0]=2
            if alerta[8]==0 and alerta[9]==0:
                est_pre[0]=0
            
            if alerta[10]==1:
                est_pre[1]=1
            if alerta[11]==1:
                est_pre[1]=2
            if alerta[10]==0 and alerta[11]==0:
                est_pre[1]=0
            
            #alerta[21]=0 if sec==0 else 0 #alerta secadores apagados
            #AC=1 if (alerta[0]==1 or alerta[1]==1 or alerta[2]==1) else 0
            AT=1 if (alerta[0]==1 or alerta[1]==1) else 0
            #AH=1 if (alerta[8]==1 or alerta[9]==1) else 0
            if (refuerzo[0]==1 or refuerzo[1]==1):
                AR=1
            #tiempos en segundos de cada unidad
            time_unit=display.obtener_segundos(hmi_time)
            
            
            #Guardar historial de alertas
            for i in range(0,len(alerta)):
                if alerta[i]==1 and alerta_hist[i]==0 and pt[14]==1:
                    alerta_hist[i]=1
                    print("alerta detectada...................")
                    try:
                        date=display.date()
                        display.guardar_registro(str(date[1])+"  "+dir_alert[i])
                    except:
                        print("NONE")
                if alerta[i]==0 and alerta_hist[i]==1 and pt[14]==1:
                    alerta_hist[i]=0
                    
            if PIN[1]==1 and PIN[6]==1 and retar==0: #{"S1": 33, "EM1": 25, "AUTO": 4, "TEMP1": 32, "TEMP2": 35} 
                retar=1
                if pt[5]==1:
                    alerta[12]=1 #retardo ambas unidades
                AR=1
                cont_retar=0
            if retar==1 and PIN[1]==0 and PIN[6]==0:
                retar=0
            #print("alertas",alerta,alerta2)
            if any(x == 1 for x in alerta) or PIN[0]==1 or PIN[5]==1:
                AG=1
                if alerta!=alerta2:
                    if pt[11]==1:
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
            if all(x == 0 for x in alerta) and PIN[0]==0 and PIN[5]==0:
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
                alerta2=[0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0]
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



#run()