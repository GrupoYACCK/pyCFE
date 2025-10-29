from .empresa import Adquirente, Emisor
from .servidor import Servidor
from pyCFE.efactura.cliente import Client
from pyCFE.efactura.efactura import SobreFactura
from pyCFE.biller.biller import Biller
from pyCFE.facturaexpress.facturaexpress import FacturaExpress
from pyCFE.facturaexpress.cliente import Client as FEClient
from datetime import datetime
from xml.dom.minidom import CDATASection


class Sobre:
    def __init__(self, vals):
        self.rutEmisor = vals.get('rutEmisor', '') or ''
        self.numero = vals.get('numero', '') or ''
        self.fecha = vals.get('fecha', '') or ''
        # self.documentoXML = vals.get('documentoXML', '')
        self.adenda = vals.get('adenda', '') or ''
        self.cfe = Documento(vals.get('documento', {}))
        self.servidor = Servidor().setServidor(vals.get('servidor', {}))
        self.cfe.servidor = self.servidor
        self.impresion = vals.get('impresion', '') or ''

    def enviarCFE(self):
        if self.servidor.codigo == 'efactura':
            cliente = Client(self.servidor.url)
            sobre = SobreFactura().getDocument(self)
            vals = {'usuario': self.servidor.usuario,
                    'clave': self.servidor.clave,
                    'rutEmisor': self.rutEmisor,
                    'sobre': sobre,
                    'impresion': self.impresion}
            estado, respuesta = cliente.recibo_venta(vals)
            return {'estado': estado, 'respuesta': respuesta}
        elif self.servidor.codigo == 'factura_express':
            cliente = FEClient(self.servidor.url)
            xml_data = FacturaExpress().xmlData(self.cfe)
            vals = {}
            vals['idEmisor'] = self.cfe.emisor.id
            documento = self.cfe
            for sucursal in self.cfe.emisor.sucursal:
                vals['codSucursal'] = str(sucursal.codigo)
                break
            vals['tipoComprobante'] = documento.tipoCFE
            vals['serie'] = documento.serie
            vals['numero'] = documento.numero
            vals['fechaEmision'] = datetime.strptime(documento.fecEmision, '%Y-%m-%d').strftime('%Y%m%d')
            if documento.fecVencimiento:
                vals['FchVenc'] = datetime.strptime(documento.fecVencimiento, '%Y-%m-%d').strftime('%Y%m%d')
            vals['formaPago'] = documento.formaPago
            # FchVenc Falta
            vals['usuario'] = self.servidor.usuario
            vals['password'] = self.servidor.clave
            cdata = CDATASection()
            cdata.data = str(xml_data, 'utf-8')
            vals['xmlData'] = cdata
            estado, respuesta = cliente.envioCfe(vals)
            return {'estado': estado, 'respuesta': respuesta}
        elif self.servidor.codigo == 'biller':
            biller = Biller(self.cfe, self.impresion)
            return biller.send_einvoice()
        else:
            return {}

    def obtenerPdfCFE(self, ducument_url_id = False, *args, **kwargs):
        if self.servidor.codigo == 'biller':
            biller = Biller(self.cfe, self.impresion)
            return biller.get_biller_pdf(ducument_url_id)
        elif self.servidor.codigo == 'factura_express':
            cliente = FEClient()
            return cliente.get_pdf(ducument_url_id)
        elif self.servidor.codigo == 'efactura':
            cliente = Client(self.servidor.url)
            estado, respuesta = cliente.get_pdf(self.servidor, *args, **kwargs)
            return {'estado': estado, 'respuesta': respuesta}
        else:
            return {}

    def consultaRUT(self, rut, *args, **kwargs):
        if self.servidor.codigo == 'efactura':
            cliente = Client(self.servidor.url)
            return cliente.consulta_rut(self.servidor, rut, *args, **kwargs)
        elif self.servidor.codigo == 'biller':
            biller = Biller(self.cfe)
            return biller.consulta_rut(rut)
        else:
            return {}

    def obtenerEstadoCFE(self, biller_id):
        if self.servidor.codigo == 'biller':
            biller = Biller(self.cfe)
            return biller.get_biller_invoice(biller_id)
        else:
            return {}

    def verificarEstadoCFE(self, numero_interno, desde=None, tipo_comprobante=None, serie=None, numero=None):
        if self.servidor.codigo == 'biller':
            biller = Biller(self.cfe)
            return biller.check_biller_invoice(numero_interno, desde, tipo_comprobante, serie, numero)
        else:
            return {}

    def compras_cfes(self, fecha_desde, fecha_hasta, rut_emisor = None):
        if self.servidor.codigo not in ['efactura', 'biller']:
            raise TypeError("El servidor no es de tipo efactura")
        if self.servidor.codigo in ['efactura']:
            cliente = Client(self.servidor.url)
            params = {
                'fechadesde': fecha_desde,
                'fechahasta': fecha_hasta,
                'rutEmisor': rut_emisor,
            }
            return cliente.compras_cfes(params, self.servidor)
        elif self.servidor.codigo in ['biller']:
            biller = Biller(self.cfe)
            return biller.get_comprobantes_recibidos(fecha_desde, fecha_hasta)

class Documento:
    def __init__(self, vals):
        self.servidor = set()  # Servidor().setServidor(vals.get('servidor', {}))
        self.emisor = Emisor(vals.get('emisor', {}))
        self.adquirente = Adquirente(vals.get('adquirente', {}))

        self.moneda = vals.get('moneda', '')
        self.tasaCambio = vals.get("tasaCambio", "")

        self.montosBrutos = vals.get("montosBrutos", '')

        self.formaPago = vals.get("formaPago", "")

        self.tipoCFE = vals.get("tipoCFE", "")
        self.serie = vals.get("serie", "")
        self.numero = vals.get("numero", "")

        self.clauVenta = vals.get("clauVenta", "")
        self.viaTransp = vals.get("viaTransp", "")
        self.modVenta = vals.get("modVenta", "")

        self.fecEmision = vals.get('fecEmision', '')
        self.fecVencimiento = vals.get('fecVencimiento', '')

        self.adenda = vals.get('adenda', '')
        self.clausulaVenta = vals.get('clausulaVenta', '')
        self.modalidadVenta = vals.get('modalidadVenta', '')
        self.viaTransporte = vals.get('viaTransporte', '')

        # items = set()
        items = []
        for item_val in vals.get('items', []):
            # items.add(Items(item_val))
            items.append(Items(item_val))
        self.items = items
        #retencionesPercepciones = set()
        retencionesPercepciones = []
        for ret_per_val in vals.get('retencionesPercepciones', []):
            # retencionesPercepciones.add(RetencionesPercepciones(ret_per_val))
            retencionesPercepciones.append(RetencionesPercepciones(ret_per_val))
        self.retencionesPercepciones = retencionesPercepciones
        # descuentos = set()
        descuentos = []
        for desc_val in vals.get('descuentos', []):
            # descuentos.add(Descuento(desc_val))
            descuentos.append(Descuento(desc_val))
        self.descuentos = descuentos
        self.mntNoGrv = round(vals.get('mntNoGrv', 0.0), 2)
        self.mntNetoIVATasaMin = round(vals.get('mntNetoIVATasaMin', 0.0), 2)
        self.mntNetoIVATasaBasica = round(vals.get('mntNetoIVATasaBasica', 0.0), 2)
        self.ivaTasaMin = round(vals.get('ivaTasaMin', 0.0), 2)
        self.ivaTasaBasica = round(vals.get('ivaTasaBasica', 0.0), 2)
        self.mntIVATasaMin = round(vals.get('mntIVATasaMin', 0.0), 2)
        self.mntIVATasaBasica = round(vals.get('mntIVATasaBasica', 0.0), 2)
        self.mntTotal = round(vals.get('mntTotal', 0.0), 2)
        self.cantLinDet = vals.get('cantLinDet', 0) or len(items)
        self.montoNF = round(vals.get('montoNF', 0.0), 2)
        self.mntPagar = round(vals.get('mntPagar', 0.0), 2)
        self.referenciaGlobal = vals.get("referenciaGlobal", "")
        self.referencia = vals.get("referencia", "")
        # referencias = set()
        referencias = []
        for ref in vals.get('referencias', []):
            # referencias.add(Referencia(ref))
            referencias.append(Referencia(ref))
        self.referencias = referencias
        self.tipo_traslado = vals.get("tipo_traslado", "")

        self.numero_interno = vals.get("numero_interno", "")
        self.numero_orden = vals.get("numero_orden", "")
        self.es_recibo = vals.get("es_recibo", False)
        self.monto = round(vals.get("monto", 0.0),2)

class Referencia:
    def __init__(self, vals):
        self.motivo = vals.get('motivo', '')
        self.tipoDocRef = vals.get('tipoDocRef', '')
        self.serie = vals.get('serie', '')
        self.numero = vals.get('numero', '')
        self.fechaCFEref = vals.get('fechaCFEref', '')
        self.padre = vals.get('padre', '')
        self.total = round(vals.get('total', 0.0),2)


class Items:

    def __init__(self, vals):
        self.indicadorFacturacion = vals.get('indicadorFacturacion', '')
        self.descripcion = vals.get('descripcion', '')
        self.cantidad = round(vals.get('cantidad', 0.0), 3)
        self.unidadMedida = vals.get('unidadMedida', 'N/A')
        self.precioUnitario = round(vals.get('precioUnitario', 0.0), 10)
        self.montoItem = round(vals.get('montoItem', 0.0), 8)
        self.codigo = vals.get("codigo", '')
        self.codProducto = vals.get('codProducto', '')
        # self.descuentoTipo = vals.get('descuentoTipo', '%')
        self.descuento = vals.get('descuento', 0.0)
        self.descuentoMonto = vals.get('descuentoMonto', 0.0)
        self.recargoMonto = vals.get('recargoMonto', 0.0)
        self.recargo = vals.get('recargo', 0.0)

class RetencionesPercepciones:

    def __init__(self, vals):
        self.codigo = vals.get('codigo', '')
        self.tasa = vals.get('tasa', 0.0)
        self.base = round(vals.get('base', 0.0),2)
        self.monto = round(vals.get('monto', 0.0), 2)
        self.indicadorFacturacion = vals.get('indicadorFacturacion', '')

class Descuento:

    def __init__(self, vals):
        self.descripcion = vals.get('descripcion', '')
        self.monto = round(vals.get('monto', 0.0), 2)
        self.indicadorFacturacion = vals.get('indicadorFacturacion', '')


class Efactura(Documento):
    def __init__(self, vals):
        super(Efactura, self).__init__(vals)


class Eticket(Documento):
    def __init__(self, vals):
        super(Eticket, self).__init__(vals)

