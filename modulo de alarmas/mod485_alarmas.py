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

def read_rs485(d):
    frame = uart.read()
    print(frame)
    try:
        if frame:
            if verificar_crc_modbus(frame):
                #print("recibido:",frame)
                if d==frame[0]:
                    if frame[1]==4: #recepcion de datos
                        reles=int((frame[4]*256)+frame[5]) #conversion de datos hex to dec
                        r = [(reles >> i) & 1 for i in range(4)] #conversion de datos dec to bin LSB
                        return 1,r,0,0
        return 0,0,0,0
    except:
        return 0,0,0,0