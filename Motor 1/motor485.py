from machine import UART,Pin
speed = 9600
uart = UART(1, speed)
uart.init(speed, bits=8, parity=None, rx=18, tx=19,timeout=20)

def rs485_available():
    return uart.any()

def send_data(a):
    crc = crc16_modbus(bytes.fromhex(a))
    frame_crc = bytes.fromhex(a) + bytes([crc & 0xFF, crc >> 8])
    print("enviado:",frame_crc)
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
    print("crc comparar:",crc_rx,crc_calc)
    return crc_rx == crc_calc

def read_rs485(d):
    frame = uart.read()
    print("data bus:",frame)
    try:
        if frame:
            if verificar_crc_modbus(frame):
                if d==frame[0]:
                    print("recibido:",frame)
                    if frame[1]==3: #solicitud de lectura
                        m1=int(frame[4]) if int(frame[4])<2 else 1
                        bu=int(frame[5]) if int(frame[5])<2 else 1
                        #dp=((frame[4] << 8) | frame[5]) - (0x10000 if frame[4] & 0x80 else 0) #conversion de datos a entero positivo o negativo
                        #if dp==0:
                        #    dp=1
                        #if dp>=6:
                        #    dp=5
                        #return 1,dp,0,0
                        return 1,m1,bu,0
                    if frame[1]==4: #recepcion de act motor y act out24v
                        m1=int(frame[4])
                        m1=1 if m1>=2 else m1
                        o1=int(frame[5])
                        o1=1 if o1>=2 else o1
                        return 2,m1,o1,0
        return 0,0,0,0
    except:
        return 0,0,0,0