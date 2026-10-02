from machine import UART,Pin
speed = 9600
uart = UART(1, speed)
uart.init(speed, bits=8, parity=None, rx=16, tx=17,timeout=60)

def rs485_available():
    return uart.any()

def send_data(a):
    crc = crc16_modbus(bytes.fromhex(a))
    frame_crc = bytes.fromhex(a) + bytes([crc & 0xFF, crc >> 8])
    #print("send 485",frame_crc)
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

def read_rs485():
    frame = uart.read()
    if frame:
        if verificar_crc_modbus(frame):
            print("ok",frame)
        else:
            print("error",frame)