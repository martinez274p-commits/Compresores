import ujson
class DATA:
    def __init__(self):
        self.adc=[0,0,0]
        self.dir=0
        self.alert=[0,0]
        self.fab=[0,0,0,0,0,0]
        self.dir_adc=['comp','max','val']
        self.dir_dir='dir'
        self.dir_alert=['co','pr']
        self.dir_fab=['comp','max','val','co','pr','dir']
        self.i=0
    
    def guardar_adc(self,a):
        adc={
            'comp':a[0], 
            'max':a[1],
            'val':a[2]
            }
        with open('adc_values.json', 'w+') as json_file:
            ujson.dump(adc, json_file)
        json_file.close()
        
    def lectura_adc(self):
        with open('adc_values.json', 'r') as json_file:
            P = ujson.load(json_file)
            for self.i in range(0,len(self.adc)):
                self.adc[self.i]=int(P[self.dir_adc[self.i]])
        json_file.close()
        return self.adc
    
    def guardar_dir(self,a):
        di={
            'dir':a
            }
        with open('dir_hex.json', 'w+') as json_file:
            ujson.dump(di, json_file)
        json_file.close()
        
    def lectura_dir(self):
        with open('dir_hex.json', 'r') as json_file:
            P = ujson.load(json_file)
            self.dir=int(P[self.dir_dir])
        json_file.close()
        return self.dir
    
    def guardar_alertas(self,a):
        alertas={
            'co':a[0], 
            'pr':a[1]
            }
        with open('alertas.json', 'w+') as json_file:
            ujson.dump(alertas, json_file)
        json_file.close()
        
    def lectura_alertas(self):
        with open('alertas.json', 'r') as json_file:
            P = ujson.load(json_file)
            for self.i in range(0,len(self.alert)):
                self.alert[self.i]=int(P[self.dir_alert[self.i]])
        json_file.close()
        return self.alert
        
    def lectura_fabrica(self):
        with open('fabrica.json', 'r') as json_file:
            P = ujson.load(json_file)
            for self.i in range(0,len(self.fab)):
                self.fab[self.i]=int(P[self.dir_fab[self.i]])
        json_file.close()
        return self.fab