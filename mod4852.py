from machine import UART,Pin
speed = 9600
uart = UART(1, speed)
uart.init(speed, bits=8, parity=None, rx=18, tx=19,timeout=60)

def rs485_available():
    return uart.any()

def send_data(a):
    crc = crc16_modbus(bytes.fromhex(a))
    frame_crc = bytes.fromhex(a) + bytes([crc & 0xFF, crc >> 8])
    print("enviado:",frame_crc, hex(crc))
    uart.write(frame_crc)

def crc16_modbus(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc

def verificar_crc_modbus(frame):
    if len(frame) < 3:
        return False
    data = frame[:-2]
    crc_rx = frame[-2] | (frame[-1] << 8)
    crc_calc = crc16_modbus(data)
    #print(crc_rx,crc_calc)
    return crc_rx == crc_calc

def read_rs4851():
    frame = uart.read()
    if frame:
        if verificar_crc_modbus(frame):
            return frame
        else:
            return "crc invalido"
    else:
        return "no recibido"
    
def read_rs485(d,m):
    frame = uart.read()
    print("data bus:",frame)
    if frame:
        if verificar_crc_modbus(frame):
            print("recibido:",frame)
            if d==frame[0] and m=="PR":
                pr=((frame[7] << 8) | frame[8]) - (0x10000 if frame[7] & 0x80 else 0) #conversion de datos a entero positivo o negativo
                hu=((frame[3] << 8) | frame[4]) - (0x10000 if frame[3] & 0x80 else 0)
                te=((frame[5] << 8) | frame[6]) - (0x10000 if frame[5] & 0x80 else 0)
                #print("val:",pr,hu,te)
                return d,pr/10,hu/10,te/10,0,0
            if d==frame[0] and m=="SC":
                co=((frame[4] << 8) | frame[5]) - (0x10000 if frame[4] & 0x80 else 0)
                pr=((frame[6] << 8) | frame[7]) - (0x10000 if frame[6] & 0x80 else 0)
                s1=int(frame[2])
                s2=int(frame[3])
                return d,pr,co,s1,s2,0
            if d==frame[0] and frame[1]==3 and m=="M2":
                cont=int(frame[2]) if int(frame[2])<2 else 1
                sobr=int(frame[3]) if int(frame[3])<2 else 1
                temp=int(frame[4]) if int(frame[4])<2 else 1
                entr=int(frame[5]) if int(frame[5])<2 else 1
                auto=int(frame[6]) if int(frame[6])<2 else 1
                return d,temp,sobr,cont,auto,entr
            if d==frame[0] and frame[1]==4 and m=="M2":
                cont=int(frame[4]) if int(frame[4])<2 else 1
                out24=int(frame[5]) if int(frame[5])<2 else 1
                return d,cont,out24,0,0,0
            if d==frame[0] and m=="AL":
                rel=int((frame[2]*256)+frame[3])
                return d,rel,0,0,0,0
            #pendiente modulo almacenamiento sd y modulo wifi
                
        else:
            return 0,0,0,0,0,0
    return 0,0,0,0,0,0