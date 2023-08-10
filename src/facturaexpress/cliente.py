from pysimplesoap.client import SoapClient, SoapFault
from lxml import etree
import requests
from base64 import encodebytes
import re
import logging

log = logging.getLogger(__name__)


class Client(object):

    def __init__(self, url=None):
        if url:
            self._url = "?wsdl" in url and url or "%s?wsdl" % url
            self._method = 'envioCfe'
            self._connect()

    def _connect(self):

        self._client = SoapClient(wsdl=self._url, cache=None, ns='econ', namespace='http://eConectorWS/',
                                           soap_ns='soapenv', soap_server="jbossas6", trace=True)

    @staticmethod
    def _get_response(response):
        try:
            log.debug(response)
            log.debug(str(response.url))
            if response.status_code in [200, 201]:
                log.debug(response.text)
                pdf = response.content

                return {'estado': True, 'respuesta': {'pdf': str(encodebytes(pdf), 'utf-8')}}
            return {'estado': False, 'respuesta': {'error': str(response.text), 'codigo': response.status_code}}
        except Exception:
            return {'estado': False, 'respuesta': {'error': response.text, 'codigo': response.status_code}}

    def get_pdf(self, pdf_url):
        url = self.get_pdf_url(pdf_url)
        if url:
            try:
                response = requests.get(url)
                return self._get_response(response)
            except Exception:
                return {'estado': False, 'respuesta': {'error': ''}}
        else:
            return {'estado': False, 'respuesta': {'error': ''}}

    @staticmethod
    def get_pdf_url(pdf_url):
        try:
            response = requests.get(pdf_url)

            pattern = '.*<script>.*location.href.*(http.+pdf).+</script>.*'
            url_pattern = re.findall(pattern, response.text.replace('\n', ''))
            if url_pattern:
                url = url_pattern[0]
            else:
                url = False
            return url
        except Exception:
            return False

    def _call_service(self, name, params):

        try:
            service = getattr(self._client, 'envioCfe')
            response = service(**params)
            res = {}
            if response.get('return'):
                data = response.get('return')
                response_xml = etree.fromstring(data)
                if response_xml.find('.//tipoComprobante') is not None:
                    res['tipoComprobante'] = response_xml.find('.//tipoComprobante').text
                if response_xml.find('.//codigo_retorno') is not None:
                    res['codigo_retorno'] = response_xml.find('.//codigo_retorno').text
                if response_xml.find('.//nro_transaccion') is not None:
                    res['nro_transaccion'] = response_xml.find('.//nro_transaccion').text
                if response_xml.find('.//mensaje_retorno') is not None:
                    res['mensaje_retorno'] = response_xml.find('.//mensaje_retorno').text
                if response_xml.find('.//serie') is not None:
                    res['serie'] = response_xml.find('.//serie').text
                if response_xml.find('.//numero') is not None:
                    res['numero'] = response_xml.find('.//numero').text
                if response_xml.find('.//qrText') is not None:
                    res['qrText'] = response_xml.find('.//qrText').text
                if response_xml.find('.//qrFile') is not None:
                    res['qrFile'] = response_xml.find('.//qrFile').text
                if response_xml.find('.//id') is not None:
                    res['id'] = response_xml.find('.//id').text
                if response_xml.find('.//dNro') is not None:
                    res['dNro'] = response_xml.find('.//dNro').text
                if response_xml.find('.//hNro') is not None:
                    res['hNro'] = response_xml.find('.//hNro').text
                if response_xml.find('.//fecVenc') is not None:
                    res['fecVenc'] = response_xml.find('.//fecVenc').text
                if response_xml.find('.//codigoResolucion') is not None:
                    res['codigoResolucion'] = response_xml.find('.//codigoResolucion').text
                if response_xml.find('.//codigoSeguridad') is not None:
                    res['codigoSeguridad'] = response_xml.find('.//codigoSeguridad').text
                if response_xml.find('.//fechaFirma') is not None:
                    res['fechaFirma'] = response_xml.find('.//fechaFirma').text
                if response_xml.find('.//linkDocumento') is not None:
                    res['linkDocumento'] = response_xml.find('.//linkDocumento').text
                    pdf_data = self.get_pdf(response_xml.find('.//linkDocumento').text)
                    res['pdf_document'] = pdf_data.get('estado') and pdf_data.get('respuesta').get('pdf') or ''
                res['return'] = data
            else:
                return False, {'faultstring': 'No se pudo obtener la respuesta'}
            return True, res
        except SoapFault as e:
            return False, {'faultcode': e.faultcode, 'faultstring': e.faultstring}
        except Exception:
            return False, {}

    def envioCfe(self, params):
        return self._call_service('envioCfe', params)


