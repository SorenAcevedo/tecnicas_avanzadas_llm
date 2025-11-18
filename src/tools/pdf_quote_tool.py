"""
Herramienta para generar una cotización en formato PDF.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from langchain.tools import tool
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class ProductItem(BaseModel):
    """Esquema para un único producto en la cotización."""
    name: str = Field(..., description="Nombre del producto.")
    price: float = Field(..., gt=0, description="Precio unitario del producto.")
    quantity: int = Field(..., gt=0, description="Cantidad del producto.")

@tool
def pdf_quote_tool(products: List[ProductItem], grand_total: float) -> str:
    """
    Genera un archivo PDF con el detalle de una cotización y lo guarda en el servidor.

    Args:
        products: Una lista de productos, cada uno con 'name', 'price', y 'quantity'.
        grand_total: El costo total de la cotización.

    Returns:
        La ruta absoluta del archivo PDF generado o un mensaje de error.
    """
    if not products:
        return "Error: No se proporcionaron productos para generar la cotización."

    # Crear directorio para las cotizaciones si no existe
    quotes_dir = Path(__file__).parent.parent.parent / "data" / "quotes"
    quotes_dir.mkdir(exist_ok=True)

    # Generar un nombre de archivo único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4()).split('-')[0]
    file_path = quotes_dir / f"cotizacion_{timestamp}_{unique_id}.pdf"

    try:
        doc = SimpleDocTemplate(str(file_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Título
        story.append(Paragraph("Cotización de Productos", styles['h1']))
        story.append(Spacer(1, 12))

        # Fecha
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 24))

        # Tabla de productos
        table_data = [
            ["Producto", "Cantidad", "Precio Unitario", "Subtotal"]
        ]
        for product in products:
            subtotal = product.price * product.quantity
            table_data.append([
                product.name,
                str(product.quantity),
                f"${product.price:,.2f}",
                f"${subtotal:,.2f}"
            ])
        
        # Fila del total
        table_data.append(["", "", Paragraph("<b>Total General</b>", styles['Normal']), Paragraph(f"<b>${grand_total:,.2f}</b>", styles['Normal'])])

        # Crear tabla y aplicar estilos
        quote_table = Table(table_data)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('BOX', (0, -1), (-1, -1), 1, colors.black),
            ('ALIGN', (0, -1), (-2, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ])
        quote_table.setStyle(style)
        
        story.append(quote_table)
        
        # Construir el PDF
        doc.build(story)

        return f"Cotización generada exitosamente en: {file_path.absolute()}"

    except Exception as e:
        return f"Error al generar el PDF: {e}"

