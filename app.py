import struct
import mod485
from time import sleep_ms
from machine import UART, Pin
import uos
#esp.osdebug(None)
uos.dupterm(None, 0)
speed = 9600
uart = UART(0, speed)
uart.init(speed, bits=8, parity=None, rx= 26, tx=27,timeout=100)

def app_uart_available():
    return uart.any()

# Funciones para comuncacion con modulo MQTT
def app_send_conf(packet):
    uart.write(packet)

def app_read_conf():
    frame = uart.read()
    print(f"Frame recibido (hex): {frame}")
    if frame:
        if int(frame[0])==0x7E:
            print("[MQTT] - Recibido:",frame)
            return frame
    return bytes([])

MOTORS_MAX = 6

# Bytes de inicio/terminacion y header
STX = 0x7E
ver = 1
typeM = 0
deviceType = 3
ETX = 0x7F

# Comandos (BYTE_COMMAND)
CMD_GET_DATA = 0x01      # Solicitar datos de monitoreo
CMD_GET_CONFIG = 0x02    # Obtener configuración
CMD_SET_CONFIG = 0x03    # Establecer configuración completa
CMD_RESET_CONFIG = 0x04  # Resetear configuración
CMD_EXPORT_CONFIG = 0x05 # Exportar configuración
CMD_IMPORT_CONFIG = 0x06 # Importar configuración
CMD_CALIBRAR = 0x07      # Calibrar sensor
CMD_CONTROL_RELE = 0x10   # Control de relé
CMD_CONTROL_BUZZER = 0x11 # Control de buzzer
CMD_ACK = 0x7F           # Respuesta OK
CMD_NACK = 0x7E          # Respuesta Error

CMD_SET_RED_ST = 0x0C   # Estados de conexión y envío de datos

CMD_GET_CALIB = 0x0B  # Comando para enviar datos de calibracion (adc, presion) en lugar de datos de telemetria

CMD_SET_CONFIG1 = 0x20 
CMD_SET_CONFIG2 = 0x21 
CMD_SET_CONFIG2 = 0x22 
CMD_GET_CONFIG1 = 0x26
CMD_GET_CONFIG2 = 0x27
CMD_GET_CONFIG3 = 0x28

format_compr_data_tel = "<HBhBbBHB" + "B"*MOTORS_MAX + "H"*(MOTORS_MAX*6) + "I"*MOTORS_MAX + "B"
format_compr_data_init = "<BBBBB"
format_compr_data_th = "<" + "B"*8 + "H"*(MOTORS_MAX*3) 
format_compr_data_sens = "<B" + "H"*6 + "H"*(MOTORS_MAX*9)
format_compr_data_alerts = "<BHHHHBHBH2B"

def crc16_modbus(data):
    """
    Calcula CRC16 Modbus
    Polinomio: 0x8005 (x^16 + x^15 + x^2 + 1)
    Valor inicial: 0xFFFF
    """
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def flatten(nested):
    """Aplana listas anidadas de cualquier profundidad."""
    out = []
    for x in nested:
        if isinstance(x, (list, tuple)):
            out.extend(flatten(x))
        else:
            out.append(x)
    return out

def chunk(seq, n):
    """Divide una secuencia en trozos de tamaño n. Devuelve lista de listas."""
    return [list(seq[i:i+n]) for i in range(0, len(seq), n)]

def pack_sw_bits(sw1, sw2, sw3, sw4, sw5, sw6, sw7, sw8,
                 sw9, sw10, sw11, sw12, sw13, sw14, sw15, sw16):
    return (
        (sw1  & 1) << 0  |
        (sw2  & 1) << 1  |
        (sw3  & 1) << 2  |
        (sw4  & 1) << 3  |
        (sw5  & 1) << 4  |
        (sw6  & 1) << 5  |
        (sw7  & 1) << 6  |
        (sw8  & 1) << 7  |
        (sw9  & 1) << 8  |
        (sw10 & 1) << 9  |
        (sw11 & 1) << 10 |
        (sw12 & 1) << 11 |
        (sw13 & 1) << 12 |
        (sw14 & 1) << 13 |
        (sw15 & 1) << 14 |
        (sw16 & 1) << 15
    )

def unpack_sw_bits(sw):
    return [(sw >> i) & 1 for i in range(16)]

def build_comp_init(n_unidades, typ_secadores, typ_temp_sens, n_temp_sens):
    try:
        return struct.pack(
            format_compr_data_init,
            0,
            n_unidades,
            typ_secadores,
            typ_temp_sens,
            n_temp_sens
        )
    except Exception as e:
        print(f"Error al construir el frame (init): {str(e)}")
        raise

def build_comp_th(th_p_out, th_p_tank, time_ref, time_sil, temp_high):
    """
    temp_high: lista plana de MOTORS_MAX*3 enteros (uint16)
    th_p_out: lista de 2 enteros (uint8)
    th_p_tank: lista de 3 enteros (uint8)
    """
    try:
        return struct.pack(
            format_compr_data_th,
            1,
            *th_p_out,
            *th_p_tank,
            time_ref,
            time_sil,
            *temp_high
        )
    except Exception as e:
        print(f"Error al construir el frame (th): {str(e)}")
        raise

def build_comp_sens(sensor_out, sensor_tank, sensor_temp):
    """
    sensor_out: lista de 3 enteros (uint16)
    sensor_tank: lista de 3 enteros (uint16)
    sensor_temp: lista plana de MOTORS_MAX*3*3 enteros (uint16)
    """
    try:
        return struct.pack(
            format_compr_data_sens,
            2,
            *sensor_out,
            *sensor_tank,
            *sensor_temp
        )
    except Exception as e:
        print(f"Error al construir el frame (): {str(e)}")
        raise

def build_comp_alerts(sw, alpha, niv_seg, act_HMI, dat_mod,
                      pet_mod, pt_max, co_max, comp_pt):
    """
    sw: entero uint16 donde:
        bit0 = sw1, bit1 = sw2, ..., bit15 = sw16
    comp_pt: lista de 2 enteros (uint8)

    Obtener sw de pack_sw_bits(sw1,sw2,...,sw16)

    Orden de los switches de alertas (bits 0 -> 15): [temp | sob | resp | ret_err | p_sal | ret_all | ret_cam | p_rocio | co | co_mod | sec | act_buzz | ref_uni | alt_uni | history | protect_temp]
    """
    try:
        return struct.pack(
            format_compr_data_alerts,
            3,
            sw,
            alpha,
            niv_seg,
            act_HMI,
            dat_mod,
            pet_mod,
            pt_max,
            co_max,
            *comp_pt
        )
    except Exception as e:
        print(f"Error al construir el frame (): {str(e)}")
        raise

def build_comp_frame(p_out, p_out_st, p_tank, p_tank_st, p_rocio, 
                     p_rocio_st, co_ppm, co_ppm_st, unidad_st, 
                     unidad_tmp, unidad_trb, secador_st):
    """
    unidad_st: lista de MOTORS_MAX enteros (uint8)
    unidad_tmp: lista plana de MOTORS_MAX*3*2 enteros (uint16)
                (o usa una lista anidada y aplánala antes)
    unidad_trb: lista de MOTORS_MAX enteros (uint32)
    """
    try:
        return struct.pack(
            format_compr_data_tel,
            p_out,
            p_out_st,
            p_tank,
            p_tank_st,
            p_rocio,
            p_rocio_st,
            co_ppm,
            co_ppm_st,
            *unidad_st,
            *unidad_tmp,
            *unidad_trb,
            secador_st
        )
    except Exception as e:
        print(f"Error al construir el frame (telemetría): {str(e)}")
        raise

def build_packet(payload, type_msg = 0):
    '''
    Construye el mensaje completo con header y CRC
    '''
    try:
        # Si payload es bytes, usarlo directamente
        if isinstance(payload, bytes):
            payload_bytes = payload
        else:
            # Intentar convertir a bytes según el tipo
            if payload is None:
                payload_bytes = b''
            elif isinstance(payload, (list,tuple)):
                payload_bytes = bytes(payload)
            elif isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            elif isinstance(payload, int):
                payload_bytes = bytes([payload])
            else:
                try:
                    payload_bytes = bytes(payload)
                except:
                    print("No se pudo convertir el payload a bytes, usando vacío")
                    payload_bytes = b''
        # Header
        hdr = bytes([ver, type_msg, deviceType, len(payload_bytes)])
        buf = hdr + payload_bytes

        # Calcular CRC
        crc = crc16_modbus(buf)

        crc_bytes = struct.pack("<H", crc)

        # Ensamblar paquete completo
        resultado = bytes([STX]) + buf + crc_bytes + bytes([ETX])

        return resultado
    except Exception as e:
        print(f"❌ Error en build_packet: {e}")
        print(f"  Tipo de error: {type(e).__name__}")
        print(f"  payload que causó error: {payload}")
        print(f"  tipo de payload: {type(payload)}")
        # Retornar un paquete mínimo en caso de error
        return bytes([STX, ver, typeM, deviceType, 0, 0, 0, ETX])

def send_simple_command(type):
    if type == "red":
        payload = struct.pack("<B", CMD_SET_RED_ST)
        packet = build_packet(payload=payload, type_msg=1)
        app_send_conf(packet)

def send_ack_nack(response):
    if response:
        payload = struct.pack("<B", CMD_ACK)
    else:
        payload = struct.pack("<B", CMD_NACK)
    packet = build_packet(payload=payload,type_msg=1)
    app_send_conf(packet)

def process_command(data):
    try:
        if len(data) < 2:
            return
        stx_pos = -1
        for i in range(len(data)):
            if data[i] == 0x7E:
                stx_pos = i
                break
        
        if stx_pos == -1:
            return
        if stx_pos > 0:
            data = data[stx_pos:]
        etx_pos = -1
        for i in range(len(data)):
            if data[i] == 0x7F:
                etx_pos = i
                break
        
        if etx_pos == -1:
            return
        
        paquete = data[:etx_pos+1]
        
        return procesar_comando_recibido(paquete)
    except Exception as e:
        #print(f'Error al leer trama de datos recibida: {str(e)}')
        return {'type': 'error', 'msg': str(e)}
    
def procesar_comando_recibido(packet):
    try:
        packet_type, byte_command, payload, crc_ok = parse_packet(packet)
        if packet_type is None:
            #print('No se pudo parsear el paquete')
            return {'type': 'error', 'msg': 'Paquete no Parseado'}
        if not crc_ok:
            #print('CRC incorrecto en paquete recibido')
            return {'type': 'error', 'msg': 'CRC incorrecto'}
        if packet_type == 1 and byte_command is not None:
            return procesar_commando_especifico(byte_command, payload or [])
        else:
            #print('El paquete no es comando o no tiene byte_command')
            return {'type': 'error', 'msg': 'Paquete no es comando o no incluye byte_command'}
    except Exception as e:
        #print(f'Error al intentar procesar el comando recibido: {str(e)}')
        return {'type': 'error', 'msg': f'Error al parsear paquete: {str(e)}'}
    
def procesar_commando_especifico(byte_command, payload):
    #print(f'Comando recibido: 0x{byte_command:02X}')    
    try:
        if byte_command == CMD_CONTROL_BUZZER:
            #print('Comando de Buzzer identificado: Aplicando ...')
            return {'type': 'buzzer'}
        elif byte_command == CMD_GET_DATA:
            #print('Comando de envío de datos identificador: Enviando...')
            return {'type': 'get_data'}
        elif byte_command == CMD_GET_CONFIG:
            return {'type': 'get_config_init'}
        elif byte_command == CMD_GET_CONFIG1:
            #print('Comando de envío de configuración identificado: Enviando...')
            return {'type': 'get_config_th'}
        elif byte_command == CMD_GET_CONFIG2:
            return {'type': 'get_config_sensors'}
        elif byte_command == CMD_GET_CONFIG3:
            return {'type': 'get_config_alerts'}
        elif byte_command == CMD_GET_CONFIG or byte_command == CMD_GET_CONFIG1 or byte_command == CMD_GET_CONFIG2 or byte_command == CMD_GET_CONFIG3 or byte_command == CMD_SET_RED_ST:
            try:
                payload_bytes = bytes(payload)
                if byte_command == CMD_GET_CONFIG:
                    #return parse_comp_init(payload_bytes) # Descomentar esta linea si se requiere modificar la configuracion INIT
                    return {'type': 'warning', 'msg': 'No se tiene permitido modificar estos parametros'}
                if byte_command == CMD_GET_CONFIG1:
                    return parse_comp_thresholds(payload_bytes)
                if byte_command == CMD_GET_CONFIG2:
                    return parse_comp_sensors(payload_bytes)
                if byte_command == CMD_GET_CONFIG3:
                    return parse_comp_alerts(payload_bytes)
                if byte_command == CMD_SET_RED_ST:
                    return parse_comm_st(payload_bytes)
            except Exception as e:
                return {'type': 'error', 'msg': f'Error procesando payload: {str(e)}'}
        else:
            #print('Comando no reconocido')
            return {'type': 'error', 'msg': 'Comando desconocido'}
    except Exception as e:
        print(f'Error al procesar el comando especifico: {str(e)}')
        return {'type': 'error', 'msg': str(e)}
    
def parse_packet(data):
    try:
        if data is None or len(data) < 6:
            print(f"Longitud de datos no valida (<6): {len(data)}")
            return None, None, None, False
        
        if data[0] != 0x7E or data[-1] != 0x7F:
            print(f"No hay bytes de inicio/fin: {data}")
            return None, None, None, False
        
        ver = data[1]
        packet_type = data[2]
        dev_typ = data[3]
        length = data[4]
        
        expected_len = 5 + length + 3
        print(bytes(data))
        if len(data) != expected_len:
            print(f"Longitud de datos no valida ({expected_len} esperado): {len(data)}")
            return None, None, None, False
        
        payload = data[5:5+length]
        crc_recibido = struct.unpack("<H", data[5+length:5+length+2])[0]
        
        buf = data[1:5+length]
        crc_calculado = crc16_modbus(buf)
        crc_ok = (crc_recibido == crc_calculado)
        
        if packet_type == 1 and length >= 1:
            byte_command = payload[0]
            command_payload = list(payload[1:]) if length > 1 else []
            print(f"Datos válidos: {packet_type} | {byte_command} | {command_payload} | {crc_ok}")
            return packet_type, byte_command, command_payload, crc_ok
        else:
            print(f"Datos no válidos: {packet_type} | {byte_command} | {payload} | {crc_ok}")
            return packet_type, None, list(payload) if payload else [], crc_ok
    except Exception as e:
        print(f'Error parseando paquete: {str(e)}')
        return None, None, None, False

def parse_comp_init(data: bytes):
    try:
        type_, n_unidades, typ_secadores, typ_temp_sens, n_temp_sens = struct.unpack(format_compr_data_init, data)
        if type_ != 0:
            return {'type': 'error', 'msg': f'[INIT] Tipo de configuracion distinto al esperado: {str(type_)}'}
        
        return {
            "n_unidades": n_unidades,           # Escalar
            "typ_secadores": typ_secadores,     # Escalar
            "typ_temp_sens": typ_temp_sens,     # Escalar
            "n_temp_sens": n_temp_sens,         # Escalar
        }
    except Exception as e:
        return {'type': 'error', 'msg': f'[INIT] Error al desempaquetar: {str(e)}'}

def parse_comp_thresholds(data: bytes):
    try:
        t = struct.unpack(format_compr_data_th, data)
        i = 0

        type_  = t[i]; i += 1
        
        if type_ != 1:
            return {'type': 'error', 'msg': f'[TH] Tipo de configuracion distinto al esperado: {str(type_)}'}
        
        #pt_max = t[i]; i += 1
        #co_max = t[i]; i += 1

        temp_flat = t[i:i + MOTORS_MAX * 3]; i += MOTORS_MAX * 3
        temp_high = chunk(temp_flat, 3)   # [M][3]

        th_p_out  = list(t[i:i+2]); i += 2
        th_p_tank = list(t[i:i+3]); i += 3

        time_ref = t[i]; i += 1
        time_sil = t[i]; i += 1

        return {
            "type": 'cnf_th',
            #"pt_max": pt_max,           # Escalar
            #"co_max": co_max,           # Escalar
            "temp_high": temp_high,     # Arreglo [6][3]
            "th_p_out": th_p_out,       # Arreglo [2]
            "th_p_tank": th_p_tank,     # Arreglo [3]
            "time_ref": time_ref,       # Escalar
            "time_sil": time_sil,       # Escalar
        }
    except Exception as e:
        return {'type': 'error', 'msg': f'[TH] Error al desempaquetar: {str(e)}'}

def parse_comp_sensors(data: bytes):
    try:
        t = struct.unpack(format_compr_data_sens, data)
        i = 0

        type_ = t[i]; i += 1
        if type_ != 2:
            return {'type': 'error', 'msg': f'[SENS] Tipo de configuracion distinto al esperado: {str(type_)}'}

        sensor_out  = list(t[i:i+3]); i += 3
        sensor_tank = list(t[i:i+3]); i += 3

        temp_flat = t[i:i + MOTORS_MAX * 9]; i += MOTORS_MAX * 9
        # Reorganizar a [M][3][3]
        sensor_temp = []
        for u in range(MOTORS_MAX):
            base = u * 9
            sensor_temp.append([
                [temp_flat[base + 0], temp_flat[base + 1], temp_flat[base + 2]],
                [temp_flat[base + 3], temp_flat[base + 4], temp_flat[base + 5]],
                [temp_flat[base + 6], temp_flat[base + 7], temp_flat[base + 8]],
            ])

        return {
            "type": 'cnf_sens',
            "sensor_out": sensor_out,       # Arreglo [3]
            "sensor_tank": sensor_tank,     # Arreglo [3]
            "sensor_temp": sensor_temp,     # Arreglo [6][3][3]
        }
    except Exception as e:
        return {'type': 'error', 'msg': f'[SENS] Error al desempaquetar: {str(e)}'}

def parse_comp_alerts(data: bytes):
    try:
        (type_, sw, alpha, niv_seg, act_HMI,
         dat_mod, pet_mod, pt_max, co_max,
         comp_pt0, comp_pt1) = struct.unpack(format_compr_data_alerts, data)

        if type_ != 3:
            return {'type': 'error', 'msg': f'[ALERT] Tipo de configuracion distinto al esperado : {str(type_)}'}

        return {
            "type": 'cnf_alerts',
            "sw": sw,                           # Valor entero con los bits de activacion para los switches de alertas
            "sw_bits": unpack_sw_bits(sw),      # Lista con los estados individuales de los switches de alertas sw_bits[0] = sw1 (temp) ... sw_bits[15] = sw16 (protect_temp)
            "alpha": alpha,
            "niv_seg": niv_seg,
            "act_HMI": act_HMI,
            "dat_mod": dat_mod,
            "pet_mod": pet_mod,
            "pt_max": pt_max,
            "co_max": co_max,
            "comp_pt": [comp_pt0, comp_pt1],
        }
    except Exception as e:
        return {'type': 'error', 'msg': f'[ALERT] Error al desempaquetar: {str(e)}'}

def parse_comm_st(data: bytes):
    '''
    Desempaqueta los estados de conexion WiFi y MQTT
      - WiFi: 0 -> Conectado  |  1 -> Desconectado  |  3 -> Apagado       |  2 -> AP o Punto de Acceso (¡No se usa aquí!)
      - MQTT: 0 -> Conectado  |  1 -> Desconectado  |  2 -> Reconectando  |  3 -> Apagado
    '''
    try:
        (type_, wifi_st, mqtt_st) = struct.unpack('<BBB', data)
        if type_ != 4:
            return {'type': 'error', 'msg': f'[RED] Tipo de datos distinto a la esperada : {str(type_)}'}
        return {
            'type': 'red_st',
            'wifi': wifi_st,
            'mqtt': mqtt_st
        }
    except Exception as e:
        return {'type': 'error', 'msg': f'[COMM_ST] Error al desempaquetar: {str(e)}'}
