from model.InputInterface import InputInterface
'''
PROBLEMES:
    - Mida 8x8 resulta UNSAT
    - Les rutes sempre tenen la llargada de width + height
    - Més de dues rutes dona UNSAT
    - Les rutes a vegades presenten salts (1, 2, 3, 6, 7, 13...)

PREGUNTES:
    - Cal tenir inserters en mig de la ruta? 
    - Es pot fer que els inserters només alimentin als constructors?
    - Com seria tenir les tres fases en un sol model?
'''

# GRAPHIC INTERFACE #
interface = InputInterface()
