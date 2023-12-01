import logging
import requests
log = logging.getLogger(__name__)


class Client(object):

    def __init__(self, url, token=None):
        self._url = url
        self._token = token
        self._version = 'v2'
        level = logging.DEBUG
        logging.basicConfig(level=level)
        log.setLevel(level)

    def _getApiMethod(self):
        self._method = "%s/comprobantes/%s" % (self._version, self._type)

    @staticmethod
    def _get_response(response):
        try:
            log.debug(response)
            log.debug(str(response.url))
            if response.status_code in [200] and str(response.url).find('comprobantes/pdf') != -1:
                log.debug(response.text)
                return {'estado': True, 'respuesta': {'pdf': response.text}}
            res = response.json()
            log.debug(res)
            if response.status_code not in [200, 201]:
                return {'estado': False, 'respuesta': {'error': str(res), 'codigo': response.status_code}}
            return {'estado': True, 'respuesta': res}
        except Exception:
            return {'estado': False, 'respuesta': {'error': response.text, 'codigo': response.status_code}}

    @staticmethod
    def _get_header(token):
        headers = {}
        headers['Authorization'] = "Bearer %s" % token
        headers['Content-Type'] = 'application/json'
        return headers

    def send_invoice(self, token, data):
        headers = self._get_header(token)
        self._type = 'crear'
        self._getApiMethod()
        url = self._url + self._method
        log.debug(data)
        response = requests.post(url, json=data, headers=headers)
        return self._get_response(response)

    def get_pdf(self, token, id):
        headers = self._get_header(token)
        self._type = "pdf"
        self._getApiMethod()
        url = self._url + self._method
        response = requests.get("%s?id=%s" % (url, id), headers=headers, timeout=30000)
        return self._get_response(response)

    def get_invoice(self, token, id):
        headers = self._get_header(token)
        self._type = "obtener"
        self._getApiMethod()
        url = self._url + self._method
        response = requests.get("%s?id=%s" % (url, id), headers=headers)
        return self._get_response(response)

    def check_invoice(self, token, numero_interno=None, desde=None, tipo_comprobante=None, serie=None, numero=None):
        headers = self._get_header(token)
        self._type = "obtener"
        self._getApiMethod()
        url = self._url + self._method
        response = False
        if numero_interno:
            response = requests.get("%s?numero_interno=%s" % (url, numero_interno), headers=headers)
        elif serie and numero and tipo_comprobante:
            response = requests.get("%s?desde=%s&tipo_comprobante=%s&serie=%s&numero=%s" % (url, desde, tipo_comprobante, serie, numero), headers=headers)
        if response:
            return self._get_response(response)
        else:
            return {}