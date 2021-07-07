from .empresa import Adquirente, Emisor
from .servidor import Servidor
from pyCFE.efactura.cliente import Client
from pyCFE.efactura.efactura import SobreFactura

class Sobre:
    def __init__(self, vals):
        self.rutEmisor = vals.get('rutEmisor', '') or ''
        self.numero = vals.get('numero', '') or ''
        self.fecha = vals.get('fecha', '') or ''
        #self.documentoXML = vals.get('documentoXML', '')
        self.adenda = vals.get('adenda', '') or ''
        self.cfe = Documento(vals.get('documento', {}))
        self.servidor = Servidor().setServidor(vals.get('servidor', {}))
        
        self.impresion = vals.get('impresion', '')  or ''
        
    def enviarCFE(self):
        if self.servidor.codigo == 'efactura':
            cliente = Client(self.servidor.url)
            sobre = SobreFactura().getDocument(self)
            vals = {'usuario':self.servidor.usuario,
                'clave': self.servidor.clave,
                'rutEmisor': self.rutEmisor,
                'sobre': str(sobre.encode('utf-8')),
                'impresion':self.impresion}
            estado, respuesta = cliente.recibo_venta(vals)
            print(sobre)
            return {'estado':estado, 'respuesta':respuesta}
        else:
            return {}
    
class Documento:
    def __init__(self, vals):
        self.servidor = Servidor().setServidor(vals.get('servidor', {}))
        self.emisor = Emisor(vals.get('emisor', {}))
        self.adquirente = Adquirente(vals.get('adquirente', {}))
        
        self.moneda = vals.get('moneda', '')
        self.tasaCambio = vals.get("tasaCambio","")
        
        self.montosBrutos = vals.get("montosBrutos", True)
        
        self.formaPago = vals.get("formaPago","")
        
        self.tipoCFE = vals.get("tipoCFE","")
        self.serie = vals.get("serie","")
        self.numero = vals.get("numero","")
        
        self.fecEmision = vals.get('fecEmision', '')
        self.fecVencimiento = vals.get('fecVencimiento', '')
        
        self.adenda = vals.get('adenda', '')
        self.clausulaVenta = vals.get('clausulaVenta', '')
        self.modalidadVenta = vals.get('modalidadVenta', '')
        self.viaTransporte = vals.get('viaTransporte', '')
        
        items = set()
        for item_val in vals.get('items', []):
            items.add(Items(item_val))
        self.items = items
        
        self.mntNoGrv = vals.get('mntNoGrv', 0.0)
        self.mntNetoIVATasaMin = vals.get('mntNetoIVATasaMin', 0.0)
        self.mntNetoIVATasaBasica = vals.get('mntNetoIVATasaBasica', 0.0)
        self.ivaTasaMin = vals.get('ivaTasaMin', 0.0)
        self.ivaTasaBasica = vals.get('ivaTasaBasica', 0.0)
        self.mntIVATasaMin = vals.get('mntIVATasaMin', 0.0)
        self.mntIVATasaBasica = vals.get('mntIVATasaBasica', 0.0)
        self.mntTotal = vals.get('mntTotal', 0.0)
        self.cantLinDet = vals.get('cantLinDet', 0.0) or len(items)
        self.montoNF = vals.get('montoNF', 0.0)
        self.mntPagar= vals.get('mntPagar', 0.0)
        
        referencias = set()
        for ref in vals.get('referencias', []):
            referencias.add(Referencia(ref))
        self.referencias = referencias

    def enviarCFE(self):
        raise "No implementado"

class Referencia:
    def __init__(self, vals):
        self.motivo  = vals.get('motivo', '')
        self.tipoDocRef  = vals.get('tipoDocRef', '')
        self.serie  = vals.get('serie', '')
        self.numero  = vals.get('numero', '')
        self.fechaCFEref  = vals.get('fechaCFEref', '')
        

class Items:
    
    def __init__(self, vals):
        self.indicadorFacturacion = vals.get('indicadorFacturacion', '')
        self.descripcion = vals.get('descripcion', '')
        self.cantidad = round(vals.get('cantidad', 0.0), 10)
        self.unidadMedida = vals.get('unidadMedida', 'N/A')
        self.precioUnitario = round(vals.get('precioUnitario', 0.0), 10)
        self.montoItem = round(vals.get('montoItem', 0.0), 2)
        
        self.codProducto = vals.get('codProducto', '')
        self.descuentoTipo = vals.get('descuentoTipo', '%')
        self.descuento = vals.get('descuento', 0.0)
        self.recargoTipo = vals.get('recargoTipo', '$')
        self.recargo = vals.get('recargo', 0.0)

        
class Efactura(Documento):
    def __init__(self, vals):
        super(Efactura, self).__init__(vals)

class Eticket(Documento):
    def __init__(self, vals):
        super(Eticket, self).__init__(vals)

