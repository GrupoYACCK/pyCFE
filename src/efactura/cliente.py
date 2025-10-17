from lxml import etree
import sys
import logging

from zeep import Client as ZeepClient, Settings
from zeep.transports import Transport
from zeep.exceptions import Fault as SoapFault  # alias para no cambiar los except existentes

if sys.version > '3':
    unicode = str

logger = logging.getLogger(__name__)


class Client(object):

    def __init__(self, url):
        self._location = url
        self._url = "%s?wsdl" % url
        self._namespace = url
        self._soapaction = "%s/RECIBESOBREVENTA" % url
        self._method = "RECIBESOBREVENTA"
        self._soapenv = """<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://turobot.com/ws/ws_efacturainfo_ventas.php">
   <soapenv:Header/>
   <soapenv:Body>
      <ws:RECIBESOBREVENTA soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
         <usuario xsi:type="xsd:string">%s</usuario>
         <clave xsi:type="xsd:string">%s</clave>
         <rutEmisor xsi:type="xsd:string">%s</rutEmisor>
         <sobre xsi:type="ws:Sobre" xmlns:ws="http://www.turobot.com/soap/ws_efacturainfo_ventas">
            <contenido_sobre xsi:type="xsd:string"><![CDATA[%s]]></contenido_sobre>
         </sobre>
         <impresion xsi:type="xsd:int">%s</impresion>
      </ws:RECIBESOBREVENTA>
   </soapenv:Body>
</soapenv:Envelope>"""
        self._exceptions = True
        self._connect()
        self._soap_namespaces = dict(
            soap11='http://schemas.xmlsoap.org/soap/envelope/',
            soap='http://schemas.xmlsoap.org/soap/envelope/',
            soapenv='http://schemas.xmlsoap.org/soap/envelope/',
            soap12='http://www.w3.org/2003/05/soap-env',
            soap12env="http://www.w3.org/2003/05/soap-envelope"
        )

    def _connect(self):
        self._settings = Settings(strict=False, xml_huge_tree=True)
        self._transport = Transport()
        self._client = ZeepClient(self._url, transport=self._transport, settings=self._settings)

    def _call_ws(self, xml):
        logger.info(str(xml, 'utf-8') if isinstance(xml, (bytes, bytearray)) else str(xml))

        parser = etree.XMLParser(strip_cdata=False)
        root = etree.fromstring(xml if isinstance(xml, bytes) else xml.encode('utf-8'), parser)

        ns = {
            'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ws': 'http://turobot.com/ws/ws_efacturainfo_ventas.php',
            'wsi': 'http://www.turobot.com/soap/ws_efacturainfo_ventas',
        }

        body = root.find('.//soapenv:Body', namespaces=ns)
        op = body.find('.//ws:RECIBESOBREVENTA', namespaces=ns)

        usuario = op.findtext('usuario', namespaces=ns)
        clave = op.findtext('clave', namespaces=ns)
        rut_emisor = op.findtext('rutEmisor', namespaces=ns)
        contenido_sobre = op.find('.//wsi:contenido_sobre', namespaces=ns)
        contenido_sobre_text = contenido_sobre.text if contenido_sobre is not None else ''
        impresion_text = op.findtext('impresion', namespaces=ns)
        try:
            impresion = int(impresion_text) if impresion_text is not None else None
        except Exception:
            impresion = None

        # Llamada real con zeep (equivalente funcional)
        response = self._client.service.RECIBESOBREVENTA(
            usuario=usuario,
            clave=clave,
            rutEmisor=rut_emisor,
            sobre={'contenido_sobre': contenido_sobre_text},
            impresion=impresion,
        )
        return response

    def _call_service(self, name, params):
        try:
            xml = self._soapenv % (params.get('usuario'), params.get('clave'), params.get('rutEmisor'),
                                   params.get('sobre'), params.get('impresion'))
            parser = etree.XMLParser(strip_cdata=False)
            root = etree.fromstring(xml, parser)
            xml = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8')
            logger.info(str(xml, 'utf-8'))
            response = self._call_ws(xml)

            res = {}
            res['estado'] = str(getattr(response, 'estado', '') or '')
            res['codigosError'] = str(getattr(response, 'codigosError', '') or '')
            res['serie'] = str(getattr(response, 'serie', '') or '')
            res['numero'] = str(getattr(response, 'numero', '') or '')
            res['PDFcode'] = str(getattr(response, 'PDFcode', '') or '')
            res['QRcode'] = str(getattr(response, 'QRcode', '') or '')
            res['codigoSeg'] = str(getattr(response, 'codigoSeg', '') or '')
            res['CAE'] = str(getattr(response, 'CAE', '') or '')
            res['CAEserie'] = str(getattr(response, 'CAEserie', '') or '')
            res['CAEdesde'] = str(getattr(response, 'CAEdesde', '') or '')
            res['CAEhasta'] = str(getattr(response, 'CAEhasta', '') or '')
            res['CAEvto'] = str(getattr(response, 'CAEvto', '') or '')
            res['URLcode'] = str(getattr(response, 'URLcode', '') or '')
            return True, res

        except SoapFault as e:
            return False, {'faultcode': getattr(e, 'code', 'Fault'), 'faultstring': str(e)}
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
