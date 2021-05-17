
class Servidor:
    
    def __init__(self):
        self.servidores = {'efactura':'Efactura'}
    
    def getServidores(self):
        res = []
        for codigo, nombre in self.servidores.items():
            res.append((codigo,nombre))
        return res
    
    def setServidor(self, vals={}):
        self.url = vals.get('url', '')
        self.usuario = vals.get('usuario', '')
        self.clave = vals.get('clave', '')
        self.codigo = vals.get('codigo', '')
        return self