def run():
    from machine import UART,Pin,ADC
    from time import ticks_ms, ticks_diff, sleep_ms
    import mod485_alarmas
    #pines = {"R1": 23, "R2": 22,"R3": 21, "R4": 19, "R5": 18, "R6": 4, "R7": 27,"R8": 26, "R9": 25,"R10": 13}
    pines = {"R1": 23, "R2": 22,"R3": 21, "R4": 19}
    dir_pin = ["R1", "R2", "R3", "R4"]
    io = {nombre: Pin(pin, Pin.OUT) for nombre, pin in pines.items()}
    #PIN = [io[n].value() for n in dir_pin] #lectura de pines controlador
    p1=Pin(32,Pin.IN)
    p2=Pin(35,Pin.IN)
    p4=Pin(34,Pin.IN)
    p8=Pin(39,Pin.IN)
    tiempo=ticks_ms()
    val_rele=[0, 0, 0, 0]
    while True:
        dir_in=[p1.value(),p2.value(),p4.value(),p8.value()]
        dir_hex=dir_in[0]+(dir_in[1]*2)+(dir_in[2]*4)+(dir_in[3]*8)
        dir_hex = 4 if dir_hex==0 else dir_hex
        if mod485_alarmas.rs485_available():
            accion=mod485_alarmas.read_rs485(dir_hex)
            print("accion",accion)
            if accion[0]==1: #[0, 0, 1, 0, 0, 0, 0, 1, 0, 0]
                val_rele=accion[1]
                tiempo=ticks_ms()
                enviar=0
                for i in range(len(dir_pin)):
                    enviar=enviar+val_rele[i]*(2**i)
                    io[dir_pin[i]].value(val_rele[i])
                dat="0"+str(dir_hex)+"04"+f'{enviar:04x}'
                mod485_alarmas.send_data(dat)
                #print("PR:",PR)
        if ticks_diff(ticks_ms(),tiempo)>10000:
            val_rele=[0, 0, 0, 0]
            for i in range(9):
                io[dir_pin[i]].value(val_rele[i])
            io[dir_pin[9]].value(1)
            sleep_ms(100)
#run()
