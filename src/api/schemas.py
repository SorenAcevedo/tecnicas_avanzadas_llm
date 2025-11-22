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


class UpdateModelRequest(BaseModel):
    """
    Schema para actualizar la configuración del modelo.
    """

    api_key: str = Field(
        ...,
        description="API key para autenticación",
        example="my-secret-api-key"
    )
    temperature: Optional[float] = Field(
        None,
        description="Temperatura del modelo (0.0 a 2.0)",
        ge=0.0,
        le=2.0,
        example=0.7
    )
    max_tokens: Optional[int] = Field(
        None,
        description="Número máximo de tokens",
        ge=1,
        le=8192,
        example=1500
    )


class UpdateModelResponse(BaseModel):
    """
    Schema para la respuesta de actualización del modelo.
    """

    message: str = Field(
        ...,
        description="Mensaje de confirmación",
        example="Configuración del modelo actualizada exitosamente"
    )
    temperature: Optional[float] = Field(
        None,
        description="Temperatura actualizada",
        example=0.7
    )
    max_tokens: Optional[int] = Field(
        None,
        description="Max tokens actualizado",
        example=1500
    )
