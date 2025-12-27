from lxml import etree

from zeep import Client as ZeepClient, Settings
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.helpers import serialize_object

import logging

logger = logging.getLogger(__name__)


class Client(object):

    def __init__(self, url):
        self._url = url
        self._connect()

    def _connect(self):
        settings = Settings(strict=False)
        transport = Transport()
        self._client = ZeepClient(self._url, transport=transport, settings=settings)

    def _call_service(self, name, params):
        def process_response(res):
            response = serialize_object(res)
            vals = {}
            vals['estado'] = response.get('estado', '')
            vals['codigosError'] = response.get('codigosError', '')
            vals['serie'] = response.get('serie', '')
            vals['numero'] = response.get('numero', '')
            vals['PDFcode'] = response.get('PDFcode', '')
            vals['QRcode'] = response.get('QRcode', '')
            vals['codigoSeg'] = response.get('codigoSeg', '')
            vals['CAE'] = response.get('CAE', '')
            vals['CAEserie'] = response.get('CAEserie', '')
            vals['CAEdesde'] = response.get('CAEdesde', '')
            vals['CAEhasta'] = response.get('CAEhasta', '')
            vals['CAEvto'] = response.get('CAEvto', '')
            vals['URLcode'] = response.get('URLcode', '')
            return vals
        try:
            service = getattr(self._client.service, name)
            response = service(**params)
            res = process_response(response)
            return True, res
        except Fault as e:
            return False, {'faultcode': e.code, 'faultstring': e.message}
        except Exception:
            return False, {}

    def recibo_venta(self, params):
        return self._call_service('RECIBESOBREVENTA', params)

    def compras_cfes(self, params, servidor):
        def process_xml(str_xml):
            xml = etree.fromstring(str_xml.encode('utf-8'), parser=etree.XMLParser(strip_cdata=False))
            res = []
            for invoice in xml.findall('cabezal'):
                vals = {}
                vals['tipo'] = invoice.find('tipo').text
                vals['serie'] = invoice.find('serie').text
                vals['numero'] = invoice.find('num').text
                vals['pago'] = invoice.find('pago').text
                vals['fecha'] = invoice.find('fecha').text
                vals['fecha_vencimiento'] = invoice.find('vto').text == '0000-00-00' and '' or invoice.find('vto').text
                vals['rut_emisor'] = invoice.find('rutEmisor').text
                vals['moneda'] = invoice.find('moneda').text
                vals['tipo_cambio'] = invoice.find('TC').text
                vals['total_neto'] = invoice.find('bruto').text
                vals['total_iva'] = invoice.find('iva').text
                res.append(vals)
            return res

        settings = Settings(strict=False)
        transport = Transport()
        client = ZeepClient(servidor.url.replace('ws/ws_efacturainfo_ventas.php?wsdl', 'ws/ws_efacturainfo_consultas.php?wsdl'), transport=transport, settings=settings)
        params['usuario'] = servidor.usuario
        params['clave'] = servidor.clave
        response = client.service.compras_CFEs(**params)
        res = []
        try:
            xml = response.informeXML
            res = process_xml(xml)
        except Exception:
            res = []
        return res

    def  get_pdf(self, servidor, *args, **kwargs):
        def process_response(response):
            res = {}
            try:
                res['error'] = response.glosaError
            except AttributeError:
                pass
            try:
                res['pdf'] = response.PDFcode
            except AttributeError:
                pass
            return res

        settings = Settings(strict=False)
        transport = Transport()
        client = ZeepClient(
            servidor.url.replace('ws/ws_efacturainfo_ventas.php?wsdl', 'ws/ws_efacturainfo_consultas.php?wsdl'),
            transport=transport, settings=settings)
        params = {}
        params['usuario'] = servidor.usuario
        params['clave'] = servidor.clave
        params['rutReceptor'] = kwargs.get('rutReceptor')
        params['rutEmisor'] = kwargs.get('rutEmisor')
        params['tipoCFE'] = kwargs.get('tipoCFE')
        params['serieCFE'] = kwargs.get('serieCFE')
        params['numeroCFE'] = kwargs.get('numeroCFE')
        try:
            response = client.service.IMPRESION_CFE_COMPRA(**params)
            res = process_response(response)
            if res.get('error'):
                return False, res
            else:
                return True, res
        except Exception as e:
            res = {'error': str(e)}
        return res

    def consulta_rut(self, servidor, rut, *args, **kwargs):
        def process_response(response):
            res = {}
            res['RUT'] = response.RUT
            res['Denominacion'] = response.Denominacion
            res['DomicilioFiscal'] = response.DomicilioFiscal
            res['TipoContribuyente'] = response.TipoContribuyente
            res['Estado'] = response.Estado
            res['Emision'] = response.Emision
            res['Vencimiento'] = response.Vencimiento
            return res

        settings = Settings(strict=False)
        transport = Transport()
        client = ZeepClient(
            servidor.url.replace('ws/ws_efacturainfo_ventas.php?wsdl', 'ws/ws_efacturainfo_consultas.php?wsdl'),
            transport=transport, settings=settings)
        params = {}
        params['usuario'] = servidor.usuario
        params['clave'] = servidor.clave
        params['rutConsulta'] = rut
        params['rutEmisor'] = kwargs.get('rutEmisor')
        try:
            response = client.service.CONSULTA_RUT(**params)
            res = process_response(response)
        except Exception as e:
            res = {'error': str(e)}
        return res

