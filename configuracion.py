import STW_HMI
from machine import Pin, ADC, reset
import mod485
import data_value
from time import sleep_ms, ticks_ms, ticks_diff
datos=data_value.DATA()

r232=data_value.DATA()
dat232=r232.lectura_hex()
print("datos leidos config:",dat232, "config port",dat232[11],dat232[12],dat232[13],dat232[14],dat232[15])

display=STW_HMI.HMI(port=dat232[12], baudrate=dat232[11], rx=dat232[13], tx=dat232[14],timeout=dat232[15])
display.write_HMI("set_text","hscroll_label","alerta_m","Iniciando Programa...")
display.back_home()

adc34 = ADC(Pin(39))#presion hospital
adc39 = ADC(Pin(34))#presion tanque
adc36 = ADC(Pin(36))#temperatura 1
adc34.atten(ADC.ATTN_11DB)
adc39.atten(ADC.ATTN_11DB)
adc36.atten(ADC.ATTN_0DB)
adc34.width(ADC.WIDTH_12BIT)
adc39.width(ADC.WIDTH_12BIT)
adc36.width(ADC.WIDTH_12BIT)

def data_485(a,d,m,n): #dat=01030000002 d=direccion de esclavo m=nombre de modulo esclavo "PR", "SC", "M2" , "AL", "MS", "MW"
    time_out=200
    mod485.send_data(a)
    time_init=ticks_ms()
    while ticks_diff(ticks_ms(),time_init)<time_out:
        if mod485.rs485_available():
            data=mod485.read_rs485(d,m,n)
            return data
    return 0,0,0,0,0,0

def send_485(a):
    mod485.send_data(a)

def adc(a):
        a=adc34.read() if a==0 else a
        a=adc39.read() if a==1 else a
        a=adc36.read() if a==2 else a
        return a

def leer_presiones():
    return datos.lectura_presiones()

def guardar_registro(a):
    datos.guardar_registro(a)

def set_color(l,p,r,g,b,t):
    display.set_color(l,p,r,g,b,t)

def leer_sensores():
    return datos.lectura_sensores()

def leer_secadores():
    return datos.lectura_secadores()

def leer_hex():
    return datos.lectura_hex()

def leer_parametros():
    return datos.lectura_parametros()

def lectura_tiempo(b):
    return datos.lectura_tiempo(b)

def guardar_tiempo(a,b):
    return datos.guardar_tiempo(a,b)

def guardar_secadores(a):
    return datos.guardar_secadores(a)

def guardar_hex(a):
    return datos.guardar_hex(a)

def write_HMI(a,b,c,d):
    display.write_HMI(str(a),str(b),str(c),str(d))

def available():
    return display.available()

def read_HMI():
    return display.read_HMI()

def open_win(a):
    display.open_win(str(a))

def close_win(a):
    display.close_win(str(a))
    
def set_visible(a,b):
    display.set_visible(str(a),str(b))

def set_enable(a,b):
    display.set_enable(str(a),str(b))

def menu_hmi(info,p,s,v):
    if info[0]=="presiones":
        display.open_win("conf_presion")
        sleep_ms(250)
        open_presiones(p)
        return 1
    if info[0]=="sensores":
        display.open_win("conf_sen")
        sleep_ms(250)
        open_sensores(s)
        return 2
    if info[0]=="unidades":
        display.open_win("param")
        return 3
    if info[0]=="historial":
        display.open_win("Historial")
        disp_historial()
        return 4
    return v

def menu_ing(pt,m):
    dat_p=["alpha","niv_auto","act_hmi","env_mod","pet_mod","rocio","co","temp","humedad"]
    display.write_HMI("set_text","label","inf_parametros","Cargando...")
    for i in range(17):
        display.write_HMI("set_value","switch",f"sw{i+1}",str(pt[i]))
        sleep_ms(100)
    for i in range(9):
        display.write_HMI("set_value","edit",dat_p[i],str(pt[i+17]))
        sleep_ms(100)
    display.write_HMI("set_text","label","inf_parametros","")
    hex_b=0
    while True:
        if display.available()>0:
            dato=display.read_HMI()
            print(dato)
            for i in range(17):
                if dato[0]==f"sw{i+1}":
                    pt[i]=int(dato[1])
            for i in range(9):
                if dato[0]==dat_p[i]:
                    pt[i+17]=dato[1]
            for i in range(len(m)):
                if dato[0]==f"dir{i+1}":
                    m[i]=dato[1]
            if dato[0]=="siguiente":
                display.open_win("conf_param2")
                sleep_ms(100)
                for i in range(6):
                    display.write_HMI("set_text","edit",f"dir{i+1}",str(m[i]))
                    sleep_ms(100)
                for i in range(6,len(m)):
                    display.write_HMI("set_value","edit",f"dir{i+1}",str(m[i]))
                    sleep_ms(100)
                hex_b=1
            if dato[0]=="atras_mod2":
                display.close_win("conf_param2")
            if dato[0]=="atras_mod":
                display.write_HMI("set_text","label","inf_parametros","Guardando espere...")
                sleep_ms(1000)
                datos.guardar_parametros(pt)
                if hex_b==1:
                    datos.guardar_hex(m)
                display.write_HMI("set_text","label","inf_parametros","Datos guardados!")
                sleep_ms(1000)
                display.write_HMI("set_text","label","inf_parametros","Reiniciando")
                sleep_ms(1000)
                display.write_HMI("set_text","label","inf_parametros","Reiniciando.")
                sleep_ms(1000)
                display.write_HMI("set_text","label","inf_parametros","Reiniciando..")
                sleep_ms(1000)
                display.write_HMI("set_text","label","inf_parametros","Reiniciando...")
                sleep_ms(1000)
                display.write_HMI("set_text","label","inf_parametros","")
                display.close_win("conf_param") 
                reset()
                
def verificar_user(d,clav,t):
    if d[0]=="usuario":
        clav[4]=d[1]
    if d[0]=="contra":
        clav[5]=d[1]
    if d[0]=="ingresar":
        if clav[4]==None and clav[5]==None:
            display.write_HMI("set_text","label","label_inf","Sin Datos!")
        if (clav[4]==None and clav[5]==clav[3-t])or(clav[4]!=clav[2-t] and clav[5]==clav[3-t]):
            display.write_HMI("set_text","label","label_inf","Verificar Usuario")
        if (clav[4]!=clav[2-t] and clav[3-t]==None) or (clav[4]!=clav[2-t] and clav[5]!=clav[3-t]) or (clav[4]==None and clav[5]!=clav[3-t]):
            display.write_HMI("set_text","label","label_inf","Verificar Datos")
        if (clav[4]==clav[2-t] and clav[3-t]==None) or (clav[4]==clav[2-t] and clav[5]!=clav[3-t]):
            display.write_HMI("set_text","label","label_inf","Verificar Clave")
        if clav[4]==clav[2-t] and clav[5]==clav[3-t]:
            display.write_HMI("set_text","label","label_inf","Datos Correctos!")
            sleep_ms(1000)
            display.write_HMI("set_text","label","label_inf","")
            sleep_ms(50)
            display.close_win("user")
            sleep_ms(500)
            if t==2:
                return 1
            if t==0:
                return 2
            state=3 #cerrar sin cambios
            return 0
    return 0

def open_presiones(p):
    dir_conf=["edit_PHB","edit_PHA","edit_PMT","edit_PAT","edit_PPT","edit_REF","edit_SIL"]
    pres_unit=["0","1x1","2x2","3x3"]
    for i in range(len(dir_conf)):
        display.write_HMI("set_text","edit",dir_conf[i],str(p[i]))
        sleep_ms(100)
    #display.write_HMI("set_text","combo_box",dir_conf[11],pres_unit[int(p[11])])

def edit_presiones(p,info):
    dir_conf=["edit_PHB","edit_PHA","edit_PMT","edit_PAT","edit_PPT","edit_REF","edit_SIL"]
    pres_unit=["0","1x1","2x2","3x3"]
    for i in range(len(dir_conf)):
        if info[0]==dir_conf[i]:
            p[i]=info[1]
    return p

def save_presiones(p):
    display.write_HMI("set_text","label","inf_presiones","Guardando datos...")
    sleep_ms(1000)
    datos.guardar_presiones(p)
    display.write_HMI("set_text","label","inf_presiones","Datos guardados...")
    sleep_ms(1000)

def config_enable(en):
    if en=="presiones":
        dir_en=["pre_hosp","pre_tanq","mod_trabajo","sil_alarm","fecha"]
    if en=="sensores":
        dir_en=["sen_hosp","sen_tanq","com_485"]
    for i in range(len(dir_en)):
        display.set_enable(dir_en[i],"true")
        sleep_ms(100)
    display.set_enable("edit_sen","false") if en=="sensores" else None
    display.set_enable("edit_pre","false") if en=="presiones" else None
    display.close_win("user")

def open_sensores(s):
    dir_conf=['adcmin_1','adcmax_1','rango_1','adcmin_2','adcmax_2','rango_2']
    for i in range(len(dir_conf)):
        display.write_HMI("set_text","edit",dir_conf[i],str(s[i]))
        sleep_ms(100)

def edit_sensores(p,info,adc,valor,EN):
    if EN==2:
        dir_conf=['adcmin_1','adcmax_1','rango_1','adcmin_2','adcmax_2','rango_2']
        for i in range(len(dir_conf)):
            if info[0]==dir_conf[i]:
                p[i]=info[1]
        if info[0]=="text485":
            sleep_ms(50)
            mod485.send_data(str(info[1]))
            time_i=ticks_ms()
            fr=0
            while ticks_diff(ticks_ms(),time_i)<200 and fr==0:
                if mod485.rs485_available():
                    data=mod485.read_rs4851()
                    try:
                        display.write_HMI("set_text","label","info_485","Dato recibido: "+ str(data.hex()))
                    except:
                        display.write_HMI("set_text","label","info_485","Dato recibido: "+ str(data))
                    fr=1
    for i in range(0,len(adc)):
        display.write_HMI("set_text","label",f"adc_{i+1}",str(int(adc[i])))
        display.write_HMI("set_text","label",f"valor_{i+1}",str(int(valor[i])))
    return p

def save_sensores(p):
    display.write_HMI("set_text","label","inf_sensores","Guardando datos...")
    sleep_ms(1000)
    datos.guardar_sensores(p)
    display.write_HMI("set_text","label","inf_sensores","Datos guardados...")
    sleep_ms(1000)

def config_fecha(info,f):
    if info[0]=="year":
        f[0]=int(info[1])
    if info[0]=="mes":
        f[1]=int(info[1])+1
    if info[0]=="dia":
        f[2]=int(info[1])
    if info[0]=="hora":
        f[3]=int(info[1])
    if info[0]=="minuto":
        f[4]=int(info[1])
    return f 

def disp_fecha(info):
    data=[0,0,0,0,0]
    data2=[0,1,0,0,0]
    dir_fec=["Ene","Feb","Mzo","Abr","May","Jun","Jul","Agto","Sept","Oct","Nov","Dic"]
    dir_fecha=["year","mes","dia","hora","minuto"]
    if info[0]=="digit_clock1":
        s=info[1].split(" ")
        fecha=s[0].split("-")+s[1].split(":")
        print(fecha)
        for i in range(0,len(data)):
            data[i]=int(fecha[i])
        for i in range(0,len(data2)):
            sleep_ms(500)
            if i==1:
                display.write_HMI("set_text","text_selector",dir_fecha[i],str(dir_fec[int(fecha[i])-data2[i]]))
            else:
                display.write_HMI("set_text","text_selector",dir_fecha[i],str(int(fecha[i])-data2[i]))
        display.write_HMI("set_text","label","info_fecha","") 
    return data  

def guardar_fecha(f):
    display.write_HMI("set_text","label","info_fecha","guardando espere...")
    sleep_ms(1000)
    display.write_HMI("set_text","label","info_fecha","hora guardada")
    sleep_ms(1000)
    display.write_HMI("set_text","label","info_fecha","")
    display.write_HMI("set_date","digit_clock","digit_clock1",str(f[0])+"-"+str(f[1])+"-"+str(f[2])+" "+str(f[3])+":"+str(f[4]))   

def time_format(time,h): #[(0,0,0,0,0,0),0]
    time=list(time)
    if h>9:
        time[4]+=1
        time[5]=0
        h=0
        if time[4]==6 and time[5]==0:
            time[3]+=1
            time[4]=0
            time[5]=0
            if time[3]>9:
                time[2]+=1
                time[3]=0
                if time[2]==6 and time[3]==0:
                    time[1]+=1
                    time[2]=0
                    time[3]=0
                    time[4]=0
                    time[5]=0
                    if time[1]>9:
                        time[0]+=1
                        time[1]=0
                        if time[0]==9 and time[1]==9:
                            time[0]=9
                            time[1]=9 
                    
    else:
        time[5]=h
    g=str(time[0])+str(time[1])+":"+str(time[2])+str(time[3])+":"+str(time[4])+str(time[5])
    return time,h,g

def param_unidades(ind,temp,t,c,pr,point,co,sc):
    def sec(f):
        vec=[0,0,1,0,0,1,1,1]
        for i in range(4):
            if f[0]==vec[i*2] and f[1]==vec[(i*2)+1]:
                return i
    if c==3:
        dir_ind=["ind2","ind3","ind4","ind1","ind11", "ind6","ind7","ind8","ind5","ind55"] #sobre,cont,auto,temp1,temp2 
        indi=["ind_r","ind_v"]
        dir_time=["horas11","horas22","horas33"]
        dir_temp=["temp1","temp11","temp2","temp22"]
        for i in range(len(dir_ind)):
            display.write_HMI("set_image","image",dir_ind[i],str(indi[ind[i]]))
        #for i in range(4,8):
        #    display.write_HMI("set_image","image",dir_ind[i],str(indi[ind[i]]))
        #time_uni=[time_format(t[0][0],h[0]),time_format(t[1][0],h[1]),time_format(t[2][0],h[2])]
    if c==0:
        dir_time=["horas1","horas2","horas3"]
        dir_temp=["temp1","temp11","temp2","temp22"]
        display.write_HMI("set_text","label","hosp_psi",str(int(temp[0])))
        display.write_HMI("set_text","label","tanque_psi",str(int(temp[1])))
        try:
            display.write_HMI("set_text","label","P_Rocio",str(int(point)))
            display.write_HMI("set_text","label","Monoxido",str(int(co)))
            dir_sec=["secoff","sec1","sec2","sec1y2"]
            #print(sec(sc),sc)
            display.write_HMI("set_image","gif","secador",str(dir_sec[sec(sc)]))
        except:
            pass
    if c==0 or c==3:
        for i in range(len(t)): #{"S1": 33, "EM1": 25, "AUTO": 4, "TEMP1": 32, "TEMP2": 35}
            display.write_HMI("set_text","label",dir_time[i],str(t[i]))
            #display.write_HMI("set_text","label",dir_temp[i],str(int(temp[i+2])))
            if ind[(i*5)+3]==1:
                display.write_HMI("set_image","gif",dir_temp[i*2],"t_normal")
            else:
                display.write_HMI("set_image","gif",dir_temp[i*2],"t_alerta")
            if ind[(i*5)+4]==1:
                display.write_HMI("set_image","gif",dir_temp[(i*2)+1],"t_normal")
            else:
                display.write_HMI("set_image","gif",dir_temp[(i*2)+1],"t_alerta")

def disp_historial():
    hist=datos.leer_historial()
    print(hist)
    for i in range (1,37):
        display.write_HMI("set_text","label",f"h{i}",hist[i])
        sleep_ms(50)
    display.write_HMI("set_text","label","ciclos",str(hist[0]))

def save_time_unit(uni,save_time,h_data):
        for i in range(1,4):
            if uni==f"U{i}":
                if save_time==1:
                    datos.guardar_tiempo(h_data,i)
                    save_time=0
        return save_time

def operacion(f,cambio,m): #modos=[ON_M1,ON_M2,ON_M3,ON_M4],1
    print("operacion:",f,cambio,m)
    #[1,1] auto 1 auto 2 
    #if cambio!=comp: # 1  ,  3
    if f[0]==0 and f[1]==0: #Probado 1x1
        return 1,"M1,1"
    if f[0]==1 and f[1]==0: #Probado 1x1
        return 1,"M1,1"
    if f[0]==0 and f[1]==1: #Probado 1x1
        return 2,"M2,1"
    if f[0]==1 and f[1]==1:
        dat=[((2,"M2,1"),(2,"M1,1,M2,1"),(2,"M1,1,M2,1")),((1,"M1,1"),(1,"M1,1,M2,1"),(1,"M1,1,M2,1")),((1,"M1,1"),(1,"M1,1,M2,1"),(1,"M1,1,M2,1")),((1,"M1,1"),(1,"M1,1,M2,1"),(1,"M1,1,M2,1"))]
        return dat[cambio-1][m-1]

def rect_cambio(c,f,m): #yuftyjfcufvyjmhgbujkm
    if (f[0]==1 and f[1]==1) or (f[0]==0 and f[1]==1) or (f[0]==1 and f[1]==0):
        m=m-1
        m=2 if m<1 else m
        return m
    return c

def date():
    display.write_HMI("get_date","digit_clock","clock1")
    l=0
    while l<=10000:
        if display.available()>0:
            dato=display.read_HMI()
            #print(dato)
            if dato[0]=='clock1':
                return dato
        l=l+1

def ordenar_tiempos_de_menor_a_mayor(tiempos: list[str]) -> list[str]:
    def convertir_a_segundos(t: str) -> int:
        h, m, s = map(int, t.split(':'))
        return h * 3600 + m * 60 + s
    return sorted(tiempos, key=convertir_a_segundos)

def comparacion_2x2(t1,t2):
    dir_t=[1,2,2,3,1,3]
    for i in range(3):
        if (t1==dir_t[(i*2)] and t2==dir_t[(i*2)+1]) or (t1==dir_t[(i*2)+1] and t2==dir_t[(i*2)]):
            return i+1
    return 1

def obtener_menor_tiempo(tiempos: list[str],mod,f) -> int:
    t_menor=1
    tiempos_ordenados = ordenar_tiempos_de_menor_a_mayor(tiempos)
    if mod==1:
            t_menor = tiempos.index(tiempos_ordenados[0]) + 1
            for i in range(3):
                if t_menor==i+1 and f[i]==0:
                    t_menor = tiempos.index(tiempos_ordenados[1]) + 1
    if mod==2:
        t_menor = comparacion_2x2(tiempos.index(tiempos_ordenados[0]) + 1,tiempos.index(tiempos_ordenados[1]) + 1)
    return t_menor