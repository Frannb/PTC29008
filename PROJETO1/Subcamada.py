from poller import Callback

class Subcamada(Callback):
    def __init__(self, file_object, tout):
        Callback.__init__(self, file_object, tout)
        self.upper = None
        self.lower = None

    def envia(self, msg):
        raise NotImplemented("Abstrato")

    def recebe(self, quadro):
        raise NotImplemented("Abstrato")

    def conecta(self, subcamada):
        self.upper = subcamada
        subcamada.lower = self
