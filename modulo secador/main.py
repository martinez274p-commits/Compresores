import main_secador
import machine
import time
try:
    print("run")
    main_secador.run()
except:
    import machine
    import time
    print("Error :(")
    time.sleep_ms(4000)
    machine.reset()