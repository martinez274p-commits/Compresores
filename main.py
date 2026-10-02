import main_compre_v5_nfpa_rev2
import machine
import time
try:
    print("run")
    main_compre_v5_nfpa_rev2.run()
except:
    import machine 
    import time
    import STW_HMI
    display=STW_HMI.HMI(port=2, baudrate=115200, rx=16, tx=17,timeout=10)
    print("Error :(")
    display.write_HMI("set_text","hscroll_label","mensaje","Error :( Reiniciando...")
    time.sleep_ms(4000)
    machine.reset()