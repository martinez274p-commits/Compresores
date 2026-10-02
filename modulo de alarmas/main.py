import main_alarmas
import machine
import time
try:
    print("run")
    main_alarmas.run()
except:
    import machine
    import time
    print("Error :(")
    time.sleep_ms(4000)
    machine.reset()