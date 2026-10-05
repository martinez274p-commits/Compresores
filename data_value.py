import ujson
class DATA:
    def __init__(self):
        self.presion=[0,0,0,0,0, 0,0]
        self.sec=[0,0]
        self.module=["","","","","","", 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.calibracion=[0,0,0,0,0 ,0]
        self.vec_time=[0,0,0,0,0,0,0]
        self.param=[0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0]
        self.dir_time=['h1','h2','h3','h4','h5','h6','h7']
        self.dir_pre=['PHB','PHA','PMT','PAT','PPT','REF','SIL']
        self.dir_sec=['SEC1','SEC2']
        self.dir_mod=['PR','M2','M3','M4','SC','MA','BR1','P1','RX1','TX1','TO1','BR2','P2','RX2','TX2','TO2','T1','T2','H1','H2','PR1','PR2']
        self.dir_sen=['min_1','max_1','val_1','min_2','max_2','val_2']
        self.dir_par=['T','SA','REDA','PDS','PDT', 'RTUO','RCU','PDR','NDC','CDM', 'SS','AB','RDU','ADU','GH', 'PPT','A','NSA','ADH','REDM', 'TPM','PDRM','NDCM','CT','CH']     
        self.i=0
    
    def guardar_hex(self,a):
        hexm = dict(zip(self.dir_mod, a))
        with open('dirmod485.json', 'w') as json_file:
            ujson.dump(hexm, json_file)
        json_file.close()
    
    def lectura_hex(self):
        with open('dirmod485.json', 'r') as json_file:
            P = ujson.load(json_file)
            for self.i in range(0,len(self.dir_mod)):
                self.module[self.i]=P[self.dir_mod[self.i]]
        json_file.close()
        return self.module
    
    def guardar_secadores(self,a):
        secadores = dict(zip(self.dir_sec, a))
        with open('secadores.json', 'w') as json_file:
            ujson.dump(secadores, json_file)
        json_file.close()
    
    def lectura_secadores(self):
        with open('secadores.json', 'r') as json_file:
            P = ujson.load(json_file)
            for self.i in range(0,len(self.dir_sec)):
                self.sec[self.i]=int(P[self.dir_sec[self.i]])
        json_file.close()
        return self.sec
    
    def guardar_presiones(self,a):
        presiones = dict(zip(self.dir_pre, a))
        with open('presiones.json', 'w') as json_file:
            ujson.dump(presiones, json_file)
        json_file.close()
        
    def lectura_presiones(self):
        with open('presiones.json', 'r') as json_file:
            P = ujson.load(json_file)
            for self.i in range(0,len(self.dir_pre)):
                self.presion[self.i]=int(P[self.dir_pre[self.i]])
        json_file.close()
        return self.presion
    
    def guardar_parametros(self,a):
        param = dict(zip(self.dir_par, a))
        with open('parametros.json', 'w') as json_file:
            ujson.dump(param, json_file)
        json_file.close()
        
    def lectura_parametros(self):
        with open('parametros.json', 'r') as json_file:
            P = ujson.load(json_file)
            for self.i in range(0,len(self.param)):
                self.param[self.i]=P[self.dir_par[self.i]]
        json_file.close()
        return self.param
    
    def guardar_sensores(self,a):
        presiones = dict(zip(self.dir_sen, a))
        with open('calibracion.json', 'w') as json_file:
            ujson.dump(presiones, json_file)
        json_file.close()

    def lectura_sensores(self):
        with open('calibracion.json', 'r') as json_file:
            P = ujson.load(json_file)
            for self.i in range(0,len(self.dir_sen)):
                self.calibracion[self.i]=int(P[self.dir_sen[self.i]])
        json_file.close()
        return self.calibracion
    
    def guardar_tiempo(self,a,d):
        d=d-1
        dir_time=['time1.json','time2.json','time3.json']
        time = {
            'h1':a[0][0],
            'h2':a[0][1],
            'h3':a[0][2],
            'h4':a[0][3],
            'h5':a[0][4],
            'h6':a[0][5],
            'h7':a[1]
            }
        with open(dir_time[d], 'w+') as json_file:
            ujson.dump(time, json_file)
        json_file.close()

    def lectura_tiempo(self,d):
        d=d-1
        dir_time=['time1.json','time2.json','time3.json']
        with open(dir_time[d], 'r') as json_file:
            self.mod = ujson.load(json_file)
            self.i=0
            for self.i in range(0,7):
                self.vec_time[self.i]=int(self.mod[self.dir_time[self.i]])
        json_file.close()
        return (self.vec_time[0],self.vec_time[1],self.vec_time[2],self.vec_time[3],self.vec_time[4],self.vec_time[5]),self.vec_time[6]
    
    def guardar_registro(self,a): # guardar registros desplazando 1 a todos los valores y eliminando el ultimo
        self.file=open("nombre_historial.json","r")
        self.nombre=ujson.loads(self.file.read())
        self.file.close()
        self.file=open(self.nombre["nombre"]+str(self.nombre["contador"])+".json","r")
        self.datos=ujson.loads(self.file.read())
        self.file.close()
        self.contador=int(self.datos["0"])+1
        self.datos["0"]=self.contador
        print("contador de registros=",self.contador)
        for i in range(1,37):
            self.datos[str(37-i)]=self.datos[str(36-i)]
        self.datos["1"]=a
        if self.contador>=50000: #limite seguro de registros en memoria generando un nuevo archivo
            self.datos["0"]=0
            self.nombre["contador"]=self.nombre["contador"]+1
            self.nuevo2=str(self.nombre).replace("'",'"')
            self.file=open("nombre_historial.json","w")
            self.file.write(self.nuevo2)
            self.file.close()
        self.nuevo=str(self.datos).replace("'",'"')
        self.file=open(self.nombre["nombre"]+str(self.nombre["contador"])+".json","w")
        self.file.write(self.nuevo)
        self.file.close()

    def leer_historial(self): # leer el historial y regresar todos los valores en una lista ordenados del 1 al 36
        self.file=open("nombre_historial.json","r")
        self.nombre=ujson.loads(self.file.read())
        self.file.close()
        self.file=open(self.nombre["nombre"]+str(self.nombre["contador"])+".json","r")
        self.datos=ujson.loads(self.file.read())
        self.file.close()
        self.h=["","","","","","","","","","" ,"","","","","","","","","","", "","","","","","","","","","", "","","","","","",""]
        for i in range(0,37):
            self.a=str(i)
            self.h[i]=self.datos[self.a]
        return self.h # datos del 0 - 20
    