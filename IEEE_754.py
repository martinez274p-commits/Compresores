def IEEE(data):
    flt=data
    ieee=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range(0,32):
        ieee[i]=int(flt[i])
    signo=int(ieee[0])
    exponente=0
    mantis=1
    for i in range(0,8):
        if int(ieee[i+1])==0 and (7-i)==0:
            break
        else:
            exponente=exponente+((int(ieee[i+1])*2)**(7-i))
    dec=exponente-127
    for i in range(9,32):
        try:
            mantis=mantis+((int(ieee[i])*2)**(-(i-8)))
        except:
            None
    resultado=mantis*(2**dec)
    return resultado
    
