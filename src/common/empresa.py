
class Sucursal:
    def __init__(self, vals):
        self.direccion = (vals.get('direccion', '') or '').strip()
        self.ciudad = (vals.get('ciudad', '') or '').strip()
        self.departamento = (vals.get('departamento', '') or '').strip()
        self.codPais = (vals.get('codPais', '') or '').strip()
        self.codigo = (vals.get('codigo', '') or '').strip()
    
class Empresa:
    
    def __init__(self, vals):
        self.nombre = (vals.get('nombre', '') or '').strip()
        self.nomComercial = (vals.get('nomComercial', '') or '').strip()
        self.tipoDocumento = (vals.get('tipoDocumento', '') or '').strip()
        self.numDocumento = (vals.get('numDocumento', '') or '').strip()
        self.direccion = (vals.get('direccion', '') or '').strip()
        self.ciudad = (vals.get('ciudad', '') or '').strip()
        self.departamento = (vals.get('departamento', '') or '').strip()
        self.codPais = (vals.get('codPais', '') or '').strip()
        self.nomPais = (vals.get('nomPais', '') or '').strip()
        self.nombreFantasia = (vals.get('nombreFantasia', '') or '').strip()
        sucursales = set()
        for suc in vals.get('sucursal', []):
            sucursales.add(Sucursal(suc))
        self.sucursal = sucursales
        

class Emisor(Empresa):
    
    def __init__(self, vals):
        super(Emisor, self).__init__(vals)
        self.id = vals.get('id')
            
    
class Adquirente(Empresa):
    
    def __init__(self, vals):
        super(Adquirente, self).__init__(vals)

if __name__ == '__main__':
    vals = set()
    data1 = Sucursal({})
    data2 = Sucursal({})
    vals.add(data1)
    vals.add(data2)
    for val in vals:
        if val == data1:
            print("Igual")
        if val == data2:
            print("Igual")
        
