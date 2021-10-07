from Enquadramento import Enquadramento
from Aplicacao import Aplicacao
from serial import Serial
from tun import Tun
from Arq import ARQ
import sys, time
import poller

if __name__ == "__main__":
    Timeout = 5 # 15 segundos

    # nome da porta serial informada como primeiro argumento
    # de linha de comando
    porta = Serial(sys.argv[1])

    # cria objeto Enquadramento
    enq = Enquadramento(porta, Timeout)

    # Cria objeto Aplicacao
    app = Aplicacao()

    # Objeto arq
    arq = ARQ(Timeout)
    '''Conecta as subcamadas. Deve ser feito a partir da subcamada inferior'''
    arq.conecta(app)
    enq.conecta(arq)

    # cria o Poller e registra os callbacks
    sched = poller.Poller()
    sched.adiciona(arq)
    sched.adiciona(enq)
    sched.adiciona(app)

    # entrega o controle ao Poller
    sched.despache()
