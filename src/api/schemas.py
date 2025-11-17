"""
Schemas para las solicitudes y respuestas del API relacionadas con el agente de Colgate.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """
    Schema para enviar un mensaje al agente de Colgate.
    """

    message: str = Field(
        ..., description="Mensaje a enviar al agente", example="Hola, ¿cómo estás?"
    )
    cellphone: str = Field(
        ...,
        description="Número de celular del remitente (solo números, máximo 10 caracteres)",
        example="1234567890",
        max_length=10,
        pattern="^\d{1,10}$",
    )


class SendMessageResponse(BaseModel):
    """
    Schema para la respuesta del agente de Colgate.
    """

    output: str = Field(
        ...,
        description="Respuesta generada por el agente",
        example="Hola, ¿en qué puedo ayudarte?",
    )
