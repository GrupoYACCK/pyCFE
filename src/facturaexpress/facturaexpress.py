# -*- encoding: utf-8 -*-
from lxml import etree
from datetime import datetime
from .cliente import Client
class FacturaExpress(object):

    def datosGenerales(self, documento, root):
        general = etree.SubElement(root, 'DatosGenerales')
        etree.SubElement(general, 'MntBruto').text = documento.montosBrutos
        # Revisar Fecha de Vencimiento
        if documento.fecVencimiento:
            etree.SubElement(general, 'FchVenc').text = datetime.strptime(documento.fecVencimiento, '%Y-%m-%d').strftime('%Y%m%d')
    def receptor(self, documento, root):
        adquirente = documento.adquirente
        receptor = etree.SubElement(root, 'Receptor')
        etree.SubElement(receptor, 'TipoDocRecep').text = adquirente.tipoDocumento or "3"
        etree.SubElement(receptor, 'CodPaisRecep').text = adquirente.codPais or "UY"
        etree.SubElement(receptor, 'DocRecep').text = adquirente.numDocumento or "0"
        etree.SubElement(receptor, 'RznSocRecep').text = adquirente.nombre or ''
        etree.SubElement(receptor, 'DirRecep').text = adquirente.direccion or ''
        etree.SubElement(receptor, 'CiudadRecep').text = adquirente.ciudad or ''
        etree.SubElement(receptor, 'DeptoRecep').text = adquirente.departamento or ''
        if documento.tipoCFE in ['121', '122', '123']:
            etree.SubElement(receptor, 'PaisRecep').text = adquirente.nomPais

    def item(self, documento, root):
        detalle = etree.SubElement(root, 'Detalle')
        line_number = 1
        for line in documento.items:
            item = etree.SubElement(detalle, 'Item')
            etree.SubElement(item, 'NroLinDet').text = str(line_number)
            etree.SubElement(item, 'IndFact').text = line.indicadorFacturacion
            etree.SubElement(item, 'NomItem').text = line.descripcion
            etree.SubElement(item, 'Cantidad').text = str(round(line.cantidad,3))
            etree.SubElement(item, 'UniMed').text = line.unidadMedida or 'N/A'
            etree.SubElement(item, 'PrecioUnitario').text = str(round(line.precioUnitario,2))
            # Revisar Descuentos
            if line.descuento:
                etree.SubElement(item, 'DescuentoPct').text = str(round(line.descuento, 3))
            if line.descuentoMonto:
                etree.SubElement(item, 'DescuentoMonto').text = str(round(line.descuentoMonto, 2))
            etree.SubElement(item, 'MontoItem').text = str(line.montoItem)
            line_number += 1

    def totales(self, documento, root):
        totales = etree.SubElement(root, 'Totales')
        if documento.tipoCFE in ['121', '122', '123']:
            etree.SubElement(totales, 'TpoMoneda').text = documento.moneda
            etree.SubElement(totales, 'TpoCambio').text = str(documento.tasaCambio)
            etree.SubElement(totales, 'MntExpoyAsim').text = str(documento.mntTotal)
            etree.SubElement(totales, 'MntTotal').text = str(documento.mntTotal)
            etree.SubElement(totales, 'CantLinDet').text = str(documento.cantLinDet)
            etree.SubElement(totales, 'MontoNF').text = '0.0'
            etree.SubElement(totales, 'MntPagar').text = str(documento.mntPagar)
        else:
            etree.SubElement(totales, 'TpoMoneda').text = documento.moneda
            etree.SubElement(totales, 'TpoCambio').text = str(documento.tasaCambio)
            etree.SubElement(totales, 'CantLinDet').text = str(documento.cantLinDet)
            etree.SubElement(totales, 'MntNoGrv').text = str(documento.mntNoGrv)
            etree.SubElement(totales, 'MntNetoIvaTasaMin').text = str(documento.mntNetoIVATasaMin)
            etree.SubElement(totales, 'MntNetoIVATasaBasica').text = str(documento.mntNetoIVATasaBasica)
            etree.SubElement(totales, 'IVATasaMin').text = str(int(documento.ivaTasaMin))
            etree.SubElement(totales, 'IVATasaBasica').text = str(int(documento.ivaTasaBasica))
            etree.SubElement(totales, 'MntIVATasaMin').text = str(documento.mntIVATasaMin)
            etree.SubElement(totales, 'MntIVATasaBasica').text = str(documento.mntIVATasaBasica)
            etree.SubElement(totales, 'MntTotal').text = str(documento.mntTotal)
            etree.SubElement(totales, 'MontoNF').text = str(documento.montoNF)
            etree.SubElement(totales, 'MntPagar').text = str(documento.mntPagar)

    def _getRef(self, documento, root):
        referenciam = etree.SubElement(root, 'Referencia')
        referencia = etree.SubElement(referenciam, 'Referencia')
        etree.SubElement(referencia, 'NroLinRef').text = str(len(documento.referencias))
        for ref in documento.referencias:
            etree.SubElement(referencia, 'TpoDocRef').text = ref.tipoDocRef
            etree.SubElement(referencia, 'Serie').text = ref.serie
            etree.SubElement(referencia, 'NroCFERef').text = ref.numero
            etree.SubElement(referencia, 'FechaCFEref').text = ref.fechaCFEref

    def _getDescuento(self, documento, root):
        if documento.descuentos:
            desc_global = etree.SubElement(root, 'DscRcgGlobal')
            line_number = 1
            for descuento in documento.descuentos:
                item = etree.SubElement(desc_global, 'DRG_Item')
                etree.SubElement(item, 'NroLinDR').text = str(line_number)
                etree.SubElement(item, 'TpoMovDR').text = 'D'
                etree.SubElement(item, 'GlosaDR').text = descuento.descripcion[:50]
                etree.SubElement(item, 'ValorDR').text = str(descuento.monto)
                etree.SubElement(item, 'IndFactDR').text = descuento.indicadorFacturacion
                line_number+=1
    def xmlData(self, documento):
        root = etree.Element("CFE")
        self.datosGenerales(documento, root)
        self.receptor(documento, root)
        self.item(documento, root)
        self.totales(documento, root)
        self._getDescuento(documento, root)
        etree.SubElement(root, 'Adenda').text = documento.adenda or ''
        if documento.tipoCFE in ['102', '103', '112', '113', '122', '123']:
            self._getRef(documento, root)
        return etree.tostring(root, pretty_print=True, encoding='utf-8')

