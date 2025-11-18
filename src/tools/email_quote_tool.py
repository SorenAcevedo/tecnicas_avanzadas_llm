"""
Herramienta para enviar una cotización por correo electrónico con un PDF adjunto.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from langchain.tools import tool

from src.config.settings import settings

class ProductItem(BaseModel):
    """Esquema para un único producto en la cotización."""
    name: str = Field(..., description="Nombre del producto.")
    price: float = Field(..., gt=0, description="Precio unitario del producto.")
    quantity: int = Field(..., gt=0, description="Cantidad del producto.")

@tool
def email_quote_tool(
    recipient_email: str,
    pdf_path: str,
    products: List[ProductItem],
    grand_total: float
) -> str:
    """
    Envía un correo electrónico con la cotización en formato PDF como adjunto.

    Args:
        recipient_email: La dirección de correo del destinatario.
        pdf_path: La ruta absoluta al archivo PDF de la cotización.
        products: Una lista de los productos en la cotización para el cuerpo del email.
        grand_total: El total de la cotización para el cuerpo del email.

    Returns:
        Un mensaje de confirmación o un error.
    """
    if not Path(pdf_path).is_file():
        return f"Error: El archivo PDF no se encontró en la ruta: {pdf_path}"

    # Crear el cuerpo del correo
    text_body = "<h3>Resumen de su Cotización</h3>"
    text_body += "<ul>"
    for product in products:
        subtotal = product.price * product.quantity
        text_body += f"<li>{product.name} (x{product.quantity}): ${subtotal:,.2f}</li>"
    text_body += "</ul>"
    text_body += f"<p><strong>Total General: ${grand_total:,.2f}</strong></p>"
    text_body += "<p>Gracias por su interés. Adjunto encontrará la cotización detallada en formato PDF.</p>"

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = "Su Cotización de Productos"
    msg.attach(MIMEText(text_body, 'html'))

    # Adjuntar el PDF
    try:
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=Path(pdf_path).name)
        part['Content-Disposition'] = f'attachment; filename="{Path(pdf_path).name}"'
        msg.attach(part)
    except Exception as e:
        return f"Error al adjuntar el archivo PDF: {e}"

    # Enviar el correo
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return f"Correo enviado exitosamente a {recipient_email}."
    except smtplib.SMTPAuthenticationError:
        return "Error de autenticación SMTP. Revisa las credenciales en el archivo .env."
    except Exception as e:
        # En un entorno real, se registraría el error detallado.
        # Por seguridad, no se expone el error completo al usuario final.
        return f"No se pudo enviar el correo. Por favor, verifica la configuración del servidor SMTP y la conexión."

