import main_motor
import machine
import time
try:
    print("run")
    main_motor.run()
except:
    import machine
    import time
    print("Error :(")
    time.sleep_ms(4000)
    machine.reset()