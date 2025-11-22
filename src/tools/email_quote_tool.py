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

class EmailInput(BaseModel):
    """Esquema de entrada para la herramienta de envío de cotizaciones por correo."""
    recipient_email: str = Field(..., description="La dirección de correo electrónico del destinatario.")
    pdf_path: str = Field(..., description="La ruta absoluta al archivo PDF de la cotización que se adjuntará.")
    products: List[ProductItem] = Field(..., description="Una lista de los productos incluidos en la cotización para generar el cuerpo del correo.")
    grand_total: float = Field(..., gt=0, description="El monto total de la cotización para incluir en el cuerpo del correo.")

@tool
def email_quote_tool(email_input: EmailInput) -> str:
    """
    Envía una cotización detallada por correo electrónico, adjuntando el archivo PDF correspondiente.

    Esta herramienta se utiliza para enviar al cliente el resumen de su cotización y el documento
    PDF formal. Construye un correo electrónico en formato HTML con el desglose de los productos,
    sus cantidades y subtotales, junto con el total general. El PDF generado previamente es
    adjuntado al correo.

    La configuración del servidor SMTP (servidor, puerto, usuario, contraseña) se obtiene de
    las variables de entorno, por lo que es crucial que estén correctamente configuradas.

    Args:
        email_input (EmailInput): Un objeto que contiene toda la información necesaria para el envío.
            - recipient_email (str): La dirección de correo del destinatario.
            - pdf_path (str): La ruta absoluta donde se encuentra el archivo PDF de la cotización.
            - products (List[ProductItem]): La lista de productos para el resumen en el cuerpo del correo.
            - grand_total (float): El total de la cotización para mostrar en el cuerpo del correo.

    Returns:
        str: Un mensaje de confirmación indicando si el correo fue enviado exitosamente o
             un mensaje de error detallando la causa del fallo (ej. archivo no encontrado,
             error de autenticación SMTP, etc.).
    """
    if not Path(email_input.pdf_path).is_file():
        return f"Error: El archivo PDF no se encontró en la ruta: {email_input.pdf_path}"

    # Crear el cuerpo del correo
    text_body = "<h3>Resumen de su Cotización</h3>"
    text_body += "<ul>"
    for product in email_input.products:
        subtotal = product.price * product.quantity
        text_body += f"<li>{product.name} (x{product.quantity}): ${subtotal:,.2f}</li>"
    text_body += "</ul>"
    text_body += f"<p><strong>Total General: ${email_input.grand_total:,.2f}</strong></p>"
    text_body += "<p>Gracias por su interés. Adjunto encontrará la cotización detallada en formato PDF.</p>"

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_SENDER_EMAIL
    msg['To'] = email_input.recipient_email
    msg['Subject'] = "Su Cotización de Productos"
    msg.attach(MIMEText(text_body, 'html'))

    # Adjuntar el PDF
    try:
        with open(email_input.pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=Path(email_input.pdf_path).name)
        part['Content-Disposition'] = f'attachment; filename="{Path(email_input.pdf_path).name}"'
        msg.attach(part)
    except Exception as e:
        return f"Error al adjuntar el archivo PDF: {e}"

    # Enviar el correo
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return f"Correo enviado exitosamente a {email_input.recipient_email}."
    except smtplib.SMTPAuthenticationError:
        return "Error de autenticación SMTP. Revisa las credenciales en el archivo .env."
    except Exception as e:
        # En un entorno real, se registraría el error detallado.
        # Por seguridad, no se expone el error completo al usuario final.
        return f"No se pudo enviar el correo. Por favor, verifica la configuración del servidor SMTP y la conexión."

