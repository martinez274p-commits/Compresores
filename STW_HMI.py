import machine
import ujson
import IEEE_754
class HMI:
    def __init__(self,port=2,baudrate=115200,rx=16,tx=17,timeout=20):# stop=1, rx=16, tx=17
        self.port=port
        self.baudrate=baudrate
        self.rx=rx
        self.tx=tx
        self.timeout=timeout
        self.dato=0
        self.t=0
        self.tipo=['','']
        self.tipo2=['','']
        self.nombre=""
        self.m_tr=[("label_txt",'0x10','0x60',10),("label_flt",'0x10','0x62',5),("edit_txt",'0x10','0x70',10),
            ("edit_int",'0x10','0x71',4),("edit_flt",'0x10','0x72',5),("spin_box_txt",'0x10','0xa0',10),
            ("spin_box_int",'0x10','0xa1',4),("spin_box_flt",'0x10','0xa2',5),("combo_box_txt",'0x10','0xb0',10),
            ("combo_box_int",'0x10','0xb1',4),("combo_box_flt",'0x10','0xb2',5),("mledit_txt",'0x10','0xc0',10),
            ("progress_bar_flt",'0x10','0x50',5),("progress_bar_int",'0x10','0x51',4),("progress_cir_flt",'0x10','0xe0',5),
            ("progress_cir_int",'0x10','0xe1',4),("scroll_label_txt",'0x11','0x0',10),("text_selec_txt",'0x10','0x80',10),
            ("text_selec_int",'0x10','0x81',4),("text_selec_int",'0x10','0x82',4),("slider_flt",'0x10','0x40',5),
            ("slider_flt",'0x10','0x41',5),("image_value_flt",'0x10','0x92',5),("button_int",'0x10','0x1',1),
            ("button_user_int",'0x10','0x2',2),("check_butt_int",'0x10', '0x20',1),("radio_butt1_int",'0x10','0x30',1),
            ("radio_butt2_int",'0x10','0x31',1),("switch_int",'0x10','0x10',1),("digit_clock_txt",'0x10','0xf0',10),
            ("chart_view_flt",'0x10','0xd1',5),("chart_view_int",'0x10','0xd2',4),("slide_ind_int",'0x11','0x10',4),
            ("slide_view_int",'0x11','0x20',4),("slide_menu_int",'0x11','0x30',4),("tab_button_int",'0x11','0x40',1),
            ("tab_view_int",'0x11','0x50',4),("combo_box_int",'0x10','0xb8',4),("xyaxis_min",'0x11','0x60',5),
            ("xyaxis_max",'0x11','0x61',5)]
        self.dates1=["set_value","set_width","set_height","set_move_to_page","set_snap_to_page","set_yslidable",
                     "set_xslidable","set_align_v","set_scale","set_radius","set_loop","set_capacity",
                     "set_angle","set_show_text","set_selected","set_yoyo","set_direction","set_lull",
                     "set_duration","set_max","set_min","set_step","set_draw_type","set_rotation",
                     "set_interval","set_frame","set_size","set_spacing","set_view","set_auto_play",
                     "set_start_angle","set_area","set_symbol"]
        self.dates2=["set_text","set_image","set_format","set_date","set_data"]
        self.dates3=["get_text","get_selected","get_value","get_percent","set_play","set_pause",
                     "set_stop","get_capacity","get_view","get_date","get_checked","get_min","get_max"]
        self.dates4=["set_value","set_range","set_scale","set_line","set_scroll_to","set_scroll_delta_to"]
        self.dato_json=""
        self.long=0
        self.data=0
        self.data_ftl=[0,0,0,0]
        self.data_ftl_str=""
        self.rtn_dt=["",0]
        self.d=''
        self.d1=''
        self.d2=""
        self.d3=""
        self.d4=["","","",""]
        self.aux=''
        self.cmd=0
        self.dir=0
        self.dat=0
        self.dat2=["",""]
        self.nom=""
        self.ver=0
        self.refer=0
        self.ser1=["","","","",""]
        self.ser2=["","","","",""]
        self.datos_hmi=["","","",""]
        self.serial=machine.UART(self.port,self.baudrate)
        self.serial.init(self.baudrate, bits=8, parity=None, rx=self.rx,tx=self.tx,stop=1,timeout=self.timeout)
    
    def response_data(self,dat):
        self.f=dat
        for i in range(0,40):
            self.tipo2[0]=self.m_tr[i][1]
            self.tipo2[1]=self.m_tr[i][2]
            if self.f[0]==self.tipo2[0] and self.f[1]==self.tipo2[1]:
                self.rtn_dt[0]=self.m_tr[i][0]
                self.rtn_dt[1]=self.m_tr[i][3]
                return self.rtn_dt
    
    def read_int1(self):
        self.data=int(self.dato[self.long+6])
        for i in range(1,self.long):
            self.nombre=self.nombre+chr(self.dato[i+6])
        return self.nombre,self.data
    
    def read_int4(self):
        self.data=int(self.dato[self.long+3])*16777216+int(self.dato[self.long+4])*65536+int(self.dato[self.long+5])*256+int(self.dato[self.long+6])
        for i in range(1,self.long-3):
            self.nombre=self.nombre+chr(self.dato[i+6])
        return self.nombre,self.data
    
    def read_ftl(self):
        for i in range(3,7):
            self.data_ftl[i-3]=bin(int.from_bytes(self.dato[self.long+i].to_bytes(1,'big'),'big'))
        for i in range(0,4):
            if len(self.data_ftl[i])<10:
                self.d4[i]=""
                for j in range(len(self.data_ftl[i]),10):
                    self.d4[i]=self.d4[i]+"0"
                for j in range(2,len(self.data_ftl[i])):
                    self.d4[i]=self.d4[i]+str(self.data_ftl[i][j])
            else:
                self.d4[i]=""
                for j in range(2,len(self.data_ftl[i])):
                    self.d4[i]=self.d4[i]+str(self.data_ftl[i][j])
        self.data_ftl_str=self.d4[0]+self.d4[1]+self.d4[2]+self.d4[3]
        self.data=IEEE_754.IEEE(self.data_ftl_str)
        if self.ser1[1]=="line_series" or self.ser1[1]=="bar_series":
            for i in range(1,self.long-5):
                self.nombre=self.nombre+chr(self.dato[i+6])
        else:
            for i in range(1,self.long-3):
                self.nombre=self.nombre+chr(self.dato[i+6])
        return self.nombre,self.data
    
    def read_txt(self):
        self.d3=0
        self.data_ftl_str=""
        for i in range(7,self.long+7):#21
            if self.d3==1:
                self.data_ftl_str=self.data_ftl_str+chr(self.dato[i])
            if self.dato[i]==58 and self.d3==0:
                self.d3=1
        for i in range(8,self.long+7):
            if self.dato[i]==34:
                break
            else:
                self.nombre=self.nombre+chr(self.dato[i])
        return self.nombre,self.data_ftl_str
    
    def read_HMI(self):
        self.nombre=""
        self.dato=self.serial.read()
        #print(self.dato)
        try:
            self.tipo[0]=hex(self.dato[3])
            self.tipo[1]=hex(self.dato[4])
            self.tipo_data=self.response_data(self.tipo)
            #print(self.tipo)
            self.d=int(self.dato[5])
            self.d2=int(self.dato[6])
            if self.d>=1:
                self.d=self.d*256
            self.long=self.d+self.d2
            if self.tipo_data[1]==1 or self.tipo_data[1]==2:
                return self.read_int1()
            if self.tipo_data[1]==4:
                return self.read_int4()
            if self.tipo_data[1]==5:
                return self.read_ftl()
            if self.tipo_data[1]==10:
                return self.read_txt()
        except Exception as e:
            print("Error:",e)
            return [0,0,0]
    
    def write_serial(self,d):
        self.ser2=d
        #datos enteros y flotantes
        for i in range(0,33):
            if self.ser2[0]==self.dates1[i]:
                if self.ver==0:
                    self.serial.write(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3]+b'":'+self.ser2[4]+b'}>ET')
                    #print(str(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3]+b'":'+self.ser2[4]+b'}>ET'))
                break
        #datos en texto
        for i in range(0,5):
            if self.ser2[0]==self.dates2[i]:
                self.serial.write(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3]+b'":"'+self.ser2[4]+b'"}>ET')
                #print(str(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3]+b'":"'+self.ser2[4]+b'"}>ET'))
                break
        #sin datos solo solicitud
        for i in range(0,13):
            if self.ser2[0]==self.dates3[i]:
                if self.ser2[0]=="get_value" and (self.ser2[1]=="line_series" or self.ser2[1]=="bar_series"):
                    self.serial.write(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3]+b'":'+self.ser2[4]+b'}>ET')
                else:
                    self.serial.write(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'"}>ET')
                break
        #datos enteros y flotantes con dos datos
        for i in range(0,6):
            if self.ser2[0]==self.dates4[i]:
                if self.ver==1:
                    if self.ser2[1]=="combo_box_ex" or self.ser2[1]=="spin_box":
                        self.serial.write(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3][0]+b'":'+self.ser2[4][0]+b',"'+self.ser2[3][1]+b'":"'+self.ser2[4][1]+b'"}>ET')
                    elif self.ser2[4][0]=="push":
                        self.serial.write(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3][0]+b'":"'+self.ser2[4][0]+b'","'+self.ser2[3][1]+b'":'+self.ser2[4][1]+b'}>ET')
                    else:
                        print(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3][0]+b'":'+self.ser2[4][0]+b',"'+self.ser2[3][1]+b'":'+self.ser2[4][1]+b'}>ET')
                        self.serial.write(b'ST<{"cmd_code":"'+self.ser2[0]+b'","type":"'+self.ser2[1]+b'","widget":"'+self.ser2[2]+b'","'+self.ser2[3][0]+b'":'+self.ser2[4][0]+b',"'+self.ser2[3][1]+b'":'+self.ser2[4][1]+b'}>ET')
                break
    
    def write_HMI(self,a,b,c,d=""):
        self.ser1[0]=a #accion set_text, set_value, get_text, get_value etc
        self.ser1[1]=b #tipo label,edit,button etc.
        self.ser1[2]=c #nombre del widget
        self.ser1[4]=d #dato a enviar texto, int, float range(1,10)
        self.ser1[3]=a.split("_",1)  #tipo de dato
        self.ser1[3]=self.ser1[3][1]
        self.ver=0
        if self.ser1[3]=="selected":
            self.ser1[3]=self.ser1[3]+"_index"
        if self.ser1[3]=="range":
            self.ser1[3]=["start_index","end_index"]
            self.ver=1
        if self.ser1[3]=="scale":
            self.ser1[3]=["scale_x","scale_y"]
            self.ver=1
        if self.ser1[3]=="line":
            self.ser1[3]=["show","smooth"]
            self.ver=1
        if self.ser1[3]=="area" or self.ser1[3]=="symbol":
            self.ser1[3]="show"
        if (self.ser1[1]=="combo_box_ex" or self.ser1[1]=="spin_box") and self.ser1[3]!="selected_index":
            if type(self.ser1[4])==type("mera"):
                self.ser1[3]="value"
            else:
                self.ver=1
                self.ser1[3]=["value","format"]
        if self.ser1[0]=="set_value" and (self.ser1[1]=="line_series" or self.ser1[1]=="bar_series"):
            self.ver=1
            if self.ser1[4][0]=="push":
                self.ser1[3]=["mode","value"]
            else:
                self.ser1[3]=["index","value"]
        if self.ser1[0]=="get_value" and (self.ser1[1]=="line_series" or self.ser1[1]=="bar_series"):
            self.ser1[3]="index"
        if self.ser1[3]=="start_angle":
            self.ser1[3]="angle"
        if self.ser1[3]=="xslidable" or self.ser1[3]=="yslidable" or self.ser1[3]=="snap_to_page" or self.ser1[3]=="move_to_page":
            self.ser1[3]="value"
        if self.ser1[3]=="scroll_to" or self.ser1[3]=="scroll_delta_to":
            self.ser1[3]=["xoffset","yoffset"]
            self.ver=1
        #print(self.ser1)
        self.write_serial(self.ser1)
    
    def available(self):     #funcion para verificar si hay datos en el bus
        return self.serial.any()
    
    def brightness(self,br):
        self.dir=str(br)
        self.serial.write(b'ST<{"cmd_code":"set_brightness","type":"system","brightness":'+self.dir+b'}>ET')
    
    def set_color(self,l,p,r,g,b,t):
        self.dir=str(l)
        self.tipe=str(p)
        self.num1=bytearray()
        self.num1.append(t)
        self.num1.append(r)
        self.num1.append(g)
        self.num1.append(b)
        self.num1=int.from_bytes(self.num1,'big')
        self.serial.write(b'ST<{"cmd_code":"set_color","type":"widget","widget":"'+self.dir+b'","color_object":"'+self.tipe+b'","color":'+str(self.num1)+b'}>ET')
    
    def set_enable(self,l,t):
        self.dir=str(l)
        self.dat=str(t)
        self.serial.write(b'ST<{"cmd_code":"set_enable","type":"widget","widget":"'+self.dir+b'","enable":'+self.dat+b'}>ET')
    
    def set_visible(self,l,t):
        self.dir=str(l)
        self.dat=str(t)
        self.serial.write(b'ST<{"cmd_code":"set_visible","type":"widget","widget":"'+self.dir+b'","visible":'+self.dat+b'}>ET')
    
    def set_xy(self,l,t):
        self.dir=str(l)
        self.dat2[0]=str(t[0])
        self.dat2[1]=str(t[1])
        self.serial.write(b'ST<{"cmd_code":"set_xy","type":"widget","widget":"'+self.dir+b'","x":'+self.dat2[0]+b',"y":'+self.dat2[1]+b'}>ET')
    
    def set_state(self,l,t):
        self.dir=str(l)
        self.dat=str(t)
        self.serial.write(b'ST<{"cmd_code":"set_state","type":"widget","widget":"'+self.dir+b'","state":"'+self.dat+b'"}>ET')
    
    def open_win(self,l):
        self.dir=str(l)
        self.serial.write(b'ST<{"cmd_code":"open_win","type":"window","widget":"'+self.dir+b'"}>ET')
    
    def close_win(self,l):
        self.dir=str(l)
        self.serial.write(b'ST<{"cmd_code":"close_win","type":"window","widget":"'+self.dir+b'"}>ET')
    
    def back_win_to(self,l):
        self.dir=str(l)
        self.serial.write(b'ST<{"cmd_code":"back_win_to","type":"window","widget":"'+self.dir+b'"}>ET')
    
    def back_win(self):
        self.serial.write(b'ST<{"cmd_code":"back_win","type":"window"}>ET')
    
    def back_home(self):
        self.serial.write(b'ST<{"cmd_code":"back_home","type":"window"}>ET')