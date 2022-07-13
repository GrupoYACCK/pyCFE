from pysimplesoap.client import SoapClient, SoapFault, SimpleXMLElement
from lxml import etree
import sys

if sys.version > '3':
    unicode = str
import logging

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

        self._client = SoapClient(location=self._location, action=self._soapaction, namespace=self._namespace)

        # self._client = SOAPProxy(self._url, self._namespace)

    def _call_ws(self, xml):
        xml_response = self._client.send(self._method, xml)
        logger.info(str(xml_response, 'utf-8'))
        response = SimpleXMLElement(xml_response, namespace=self._namespace,
                                    jetty=False)
        if self._exceptions and response("Fault", ns=list(self._soap_namespaces.values()), error=False):
            detailXml = response("detail", ns=list(self._soap_namespaces.values()), error=False)
            detail = None

            if detailXml and detailXml.children():
                if self.services is not None:
                    operation = self._client.get_operation(self._method)
                    fault_name = detailXml.children()[0].get_name()
                    # if fault not defined in WSDL, it could be an axis or other
                    # standard type (i.e. "hostname"), try to convert it to string
                    fault = operation['faults'].get(fault_name) or unicode
                    detail = detailXml.children()[0].unmarshall(fault, strict=False)
                else:
                    detail = repr(detailXml.children())

            raise SoapFault(unicode(response.faultcode),
                            unicode(response.faultstring),
                            detail)
        return response

    def _call_service(self, name, params):

        try:
            xml = self._soapenv % (params.get('usuario'), params.get('clave'), params.get('rutEmisor'),
                                   params.get('sobre'), params.get('impresion'))
            parser = etree.XMLParser(strip_cdata=False)
            root = etree.fromstring(xml, parser)
            xml = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8')
            logger.info(str(xml, 'utf-8'))
            # return True, call(self._url, soapenv, namespace, soapaction = self._soapaction, encoding = "UTF-8")
            # return True,  self._client.invoke(name, (), params)
            response = self._call_ws(xml)
            res = {}
            res['estado'] = str(response.estado or '')
            res['codigosError'] = str(response.codigosError or '')
            res['serie'] = str(response.serie or '')
            res['numero'] = str(response.numero or '')
            res['PDFcode'] = str(response.PDFcode or '')
            res['QRcode'] = str(response.QRcode or '')
            res['codigoSeg'] = str(response.codigoSeg or '')
            res['CAE'] = str(response.CAE or '')
            res['CAEserie'] = str(response.CAEserie or '')
            res['CAEdesde'] = str(response.CAEdesde or '')
            res['CAEhasta'] = str(response.CAEhasta or '')
            res['CAEvto'] = str(response.CAEvto or '')
            res['URLcode'] = str(response.URLcode or '')

            return True, res
            # service = getattr(self._client, name)
            # return True, service(**params)
            # return True, self._client.send("RECIBESOBREVENTA", soapenv)
        except SoapFault as e:
            return False, {'faultcode': e.faultcode, 'faultstring': e.faultstring}
        except Exception:
            return False, {}

    def recibo_venta(self, params):
        return self._call_service('RECIBESOBREVENTA', params)


