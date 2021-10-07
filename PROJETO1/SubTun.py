from Subcamada import Subcamada
from Quadro import Quadro
from tun import Tun
import sys,time

class SubTun(Subcamada):
    def __init__(self, tun):
        Subcamada.__init__(self, tun.fd)
        self._tun = tun

    def handle(self):
        proto, pkt = self._tun.get_frame()
        print('Lido:', proto, pkt)

    def handle_timeout(self):
        print('Timeout !')
