import os
from decimal import Decimal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from bd.venta import Venta

class GeneradorPDF:
    @classmethod
    def generar_ticket_venta(cls, id_venta, ruta_archivo):
        detalle = Venta.obtener_detalle_ticket(id_venta)
        if not detalle:
            return False, "No se encontró el detalle de la venta."

        try:
            ticket = detalle["ticket"]
            
            # Tamaño de ticket tipo impresora térmica (aprox 80mm de ancho)
            ancho_ticket = 80 * mm
            alto_ticket = 200 * mm 
            
            pdf = SimpleDocTemplate(
                ruta_archivo, 
                pagesize=(ancho_ticket, alto_ticket),
                rightMargin=5*mm, leftMargin=5*mm, topMargin=5*mm, bottomMargin=5*mm
            )
            
            estilos = getSampleStyleSheet()
            estilo_centrado = ParagraphStyle(name="Centrado", parent=estilos["Normal"], alignment=1, fontSize=9)
            estilo_izq = ParagraphStyle(name="Izq", parent=estilos["Normal"], alignment=0, fontSize=8)
            estilo_der = ParagraphStyle(name="Der", parent=estilos["Normal"], alignment=2, fontSize=8)

            elementos = []
            
            # Encabezado del ticket
            elementos.append(Paragraph("<b>MORENOS BARBER</b>", estilo_centrado))
            elementos.append(Paragraph("Ticket de Venta", estilo_centrado))
            elementos.append(Spacer(1, 5))
            elementos.append(Paragraph(f"Folio: <b>#{ticket['id_venta']}</b>", estilo_centrado))
            elementos.append(Paragraph(f"Fecha: {ticket['fecha_hora']}", estilo_centrado))
            elementos.append(Spacer(1, 10))
            
            # Datos del cliente y cajero
            cliente = f"{ticket.get('cliente_nombres', '')} {ticket.get('cliente_apellido', '')}".strip()
            cajero = f"{ticket.get('cajero_nombres', '')} {ticket.get('cajero_apellido', '')}".strip()
            
            elementos.append(Paragraph(f"Cliente: {cliente if cliente else 'Mostrador'}", estilo_izq))
            elementos.append(Paragraph(f"Atendió: {cajero if cajero else 'Administrador'}", estilo_izq))
            elementos.append(Spacer(1, 8))
            
            # Tabla de artículos (Cant, Concepto, Importe)
            datos_tabla = [["Cant", "Concepto", "Importe"]]
            for s in detalle["servicios"]:
                datos_tabla.append(["1", s['nombre_servicio'], f"${s['precio_cobrado']:,.2f}"])
            for p in detalle["productos"]:
                subtotal_p = p['precio_cobrado'] * p['cantidad']
                datos_tabla.append([str(p['cantidad']), p['nombre_producto'], f"${subtotal_p:,.2f}"])
            
            tabla = Table(datos_tabla, colWidths=[8*mm, 40*mm, 20*mm])
            tabla.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('ALIGN', (0,0), (0,-1), 'CENTER'), 
                ('ALIGN', (1,0), (1,-1), 'LEFT'),   
                ('ALIGN', (2,0), (2,-1), 'RIGHT'),  
                ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black), 
            ]))
            elementos.append(tabla)
            elementos.append(Spacer(1, 10))
            
            # Totales
            total_ticket = Decimal(str(ticket['total']))
            subtotal_ticket = total_ticket / Decimal("1.16")
            iva_ticket = total_ticket - subtotal_ticket
            
            elementos.append(Paragraph(f"Subtotal: ${subtotal_ticket:,.2f}", estilo_der))
            elementos.append(Paragraph(f"IVA (16%): ${iva_ticket:,.2f}", estilo_der))
            elementos.append(Paragraph(f"<b>TOTAL: ${total_ticket:,.2f}</b>", ParagraphStyle(name="Total", alignment=2, fontSize=11, fontName="Helvetica-Bold")))
            
            elementos.append(Spacer(1, 10))
            elementos.append(Paragraph(f"Método de pago: {ticket['metodo_pago']}", estilo_centrado))
            elementos.append(Spacer(1, 10))
            elementos.append(Paragraph("¡Gracias por su preferencia!", estilo_centrado))
            
            pdf.build(elementos)
            return True, "Ticket generado correctamente."
            
        except Exception as e:
            return False, f"Error al generar el PDF del ticket: {e}"