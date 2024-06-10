from .cliente import Client


class Biller:

    def __init__(self, documento=None):
        self.documento = documento

    def _get_voucher(self):
        vals = {}
        vals['tipo_comprobante'] = int(self.documento.tipoCFE)
        if self.documento.tipoCFE not in ['182']:
            if self.documento.fecVencimiento:
                vals['fecha_vencimiento'] = self.documento.fecVencimiento
            vals['forma_pago'] = self.documento.formaPago
            vals['fecha_emision'] = self.documento.fecEmision

        vals['moneda'] = self.documento.moneda
        if self.documento.moneda != "UYU":
            vals['tasa_cambio'] = self.documento.tasaCambio
        if self.documento.tipoCFE not in ['182']:
            if self.documento.tipoCFE not in ['151', '152', '153']:
                vals['montos_brutos'] = self.documento.montosBrutos == '1' and True or False
            else:
                vals['montos_brutos'] = self.documento.montosBrutos
        for sucursal in self.documento.emisor.sucursal:
            vals['sucursal'] = sucursal.codigo or "1"
            break
        vals['numero_interno'] = self.documento.numero_interno
        if self.documento.numero_orden:
            vals['numero_orden'] = self.documento.numero_orden
        return vals

    def _get_ref(self):
        vals = {}
        #vals['referencia_global'] = (self.documento.referencias and self.documento.referencias[0].serie) and 0 or 1
        #vals['razon_referencia'] = self.documento.referencias and self.documento.referencias[0].descripcion or ""
        ref_vals = []
        vals['referencia_global'] = self.documento.referenciaGlobal
        vals['razon_referencia'] = self.documento.referencia
        for ref in self.documento.referencias:
            val = {}
            val['tipo'] = ref.tipoDocRef
            val['serie'] = ref.serie
            val['numero'] = ref.numero
            ref_vals.append(val)
        vals['referencias'] = ref_vals
        return vals

    def _get_partner(self):
        vals = {}
        adquirente = self.documento.adquirente
        if not adquirente.tipoDocumento:
            vals['cliente'] = '-'
        else:
            val = {}
            val['tipo_documento'] = adquirente.tipoDocumento or "3"
            val['documento'] = adquirente.numDocumento or '0'
            val['razon_social'] = adquirente.nombre
            val['nombre_fantasia'] = adquirente.nombreFantasia

            branch = self._get_branch()
            if branch:
                val.update(branch)
            vals['cliente'] = val
        return vals

    def get_server(self):
        vals = {}
        vals['url'] = self.documento.servidor.url
        vals['token'] = self.documento.servidor.clave
        return vals

    def _get_branch(self):
        res = {}
        adquirente = self.documento.adquirente
        val = {}
        val['direccion'] = adquirente.direccion
        val['ciudad'] = adquirente.ciudad or "Montevideo"
        val['departamento'] = adquirente.departamento or "Montevideo"
        val['pais'] = adquirente.codPais or "UY"
        res['sucursal'] = val
        return res

    def _get_lines(self):
        lines = []
        for line in self.documento.items:
            vals = {}
            vals['cantidad'] = round(line.cantidad, 3)
            if line.codigo:
                vals['codigo'] = line.codigo
            vals['concepto'] = line.descripcion[:80]
            vals['precio'] = line.precioUnitario

            vals['indicador_facturacion'] = line.indicadorFacturacion

            vals['descuento_tipo'] = '$'
            if line.descuentoMonto > 0.0:
                vals['descuento_cantidad'] = round(line.descuentoMonto, 2)
            vals['recargo_tipo'] = '$'
            vals['recargo_cantidad'] = 0
            lines.append(vals)
        return {'items': lines}

    def _get_retencionesPercepciones(self):
        retencionesPercepciones = []
        for ret in self.documento.retencionesPercepciones:
            vals = {}
            vals['codigo'] = ret.codigo
            vals['tasa'] = ret.tasa
            vals['monto_sujeto'] = ret.base
            retencionesPercepciones.append(vals)
        return {'retencionesPercepciones': retencionesPercepciones}

    def get_document(self):
        documento = {}
        documento.update(self._get_voucher())
        documento.update(self._get_partner())
        if self.documento.items:
            documento.update(self._get_lines())
        if self.documento.retencionesPercepciones and self.documento.tipoCFE in ['182']:
            documento.update(self._get_retencionesPercepciones())
        if self.documento.tipoCFE in ['102', '103', '112', '113', '152', '153']:
            documento.update(self._get_ref())
        if self.documento.adenda:
            documento['adenda'] = self.documento.adenda
        if self.documento.clauVenta:
            documento['clausula_venta'] = self.documento.clauVenta
        if self.documento.modVenta:
            documento['modalidad_venta'] = self.documento.modVenta
        if self.documento.viaTransp:
            documento['via_transporte'] = self.documento.viaTransp
        return documento

    def send_einvoice(self):
        documento = self.get_document()
        client = Client(self.documento.servidor.url)
        data = client.send_invoice(self.documento.servidor.token, documento)

        if data and data.get('estado') and data.get('respuesta') and data.get('respuesta', {}).get('id'):
            try:
                invoice_data = client.get_invoice(self.documento.servidor.token, data.get('respuesta', {}).get('id'))
                if invoice_data.get('estado') and invoice_data.get('respuesta'):
                    data['respuesta']['cae'] = invoice_data.get('respuesta')[0].get('cae', {})
            except Exception:
                pass

        if data and data.get('estado') and data.get('respuesta') and data.get('respuesta', {}).get('id'):
            try:
                pdf_data = client.get_pdf(self.documento.servidor.token, data.get('respuesta', {}).get('id'))
                if pdf_data.get('estado') and pdf_data.get('respuesta'):
                    data['respuesta']['pdf'] = pdf_data.get('respuesta').get('pdf')
            except Exception:
                pass
        return data

    def get_biller_pdf(self, biller_id):

        try:
            client = Client(self.documento.servidor.url)
            pdf_data = client.get_pdf(self.documento.servidor.token, biller_id)
            return pdf_data
        except Exception:
            return {'estado': False, 'respuesta': {'error': 'Error en la consulta a biller'}}

    def get_biller_invoice(self, biller_id):

        try:
            client = Client(self.documento.servidor.url)
            invoice_data = client.get_invoice(self.documento.servidor.token, biller_id)
            return len(invoice_data) and {'estado': True, "respuesta": invoice_data[0]} or {}
        except Exception:
            return {'estado': False, 'respuesta': {'error': 'Error en la consulta a biller'}}

    def check_biller_invoice(self, numero_interno, desde=None, tipo_comprobante=None, serie=None, numero=None):
        try:
            client = Client(self.documento.servidor.url)
            invoice_data = client.check_invoice(self.documento.servidor.token, numero_interno, desde, tipo_comprobante, serie, numero)
            if type(invoice_data.get('respuesta'))==list:
                invoice_data['respuesta'] = invoice_data.get('respuesta')[0]
            return invoice_data or {}
        except Exception:
            return {'estado': False, 'respuesta': {'error': 'Error en la consulta a biller'}}