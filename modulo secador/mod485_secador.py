from machine import UART,Pin
speed = 9600
uart = UART(1, speed)
uart.init(speed, bits=8, parity=None, rx=16, tx=17,timeout=20)

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
    return crc_rx == crc_calc

def hex_to_int16(hex_str):
    return int(hex_str, 16) - (1 << 16) if int(hex_str, 16) & 0x8000 else int(hex_str, 16)

def read_rs485(d,c):
    frame = uart.read()
    try:
        if frame:
            if verificar_crc_modbus(frame):
                print("recibido:",frame)
                if d==frame[0]:
                    if frame[1]==3: #solicitud de lectura
                        pr=((frame[6] << 8) | frame[7]) - (0x10000 if frame[6] & 0x80 else 0) #conversion de datos a entero positivo o negativo
                        return 1,pr,int(frame[4]),int(frame[5])
                    if frame[1]==16:#solicitud de reescribir datos
                        if frame[3]==16: #solicitud de cambio de id
                            return 2, int((frame[6]*256)+frame[7]),0,0
                        elif frame[3]==32: #solicitud de cambio de valores adc de co
                            return 3, int((frame[6]*256)+frame[7]),int((frame[8]*256)+frame[9]),int((frame[10]*256)+frame[11])
                        elif frame[3]==37: #solicitud de cambio de alertas
                            return 4, int((frame[6]*256)+frame[7]),int((frame[8]*256)+frame[9]),0
                        elif frame[3]==48: #solicitud de reinicio de fabrica
                            return 5,0,0,0
                        else:
                            return 0,0,0,0
                if c==1:
                    b=1
                    if b==frame[0]:
                        if frame[1]==4:
                            pr=((frame[5] << 8) | frame[6]) - (0x10000 if frame[5] & 0x80 else 0)
                            return 6,pr,0,0
        return 0,0,0,0
    except:
        return 0,0,0,0