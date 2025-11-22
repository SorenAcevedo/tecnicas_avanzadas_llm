"""
Rutas API relacionadas con el LLM de Colgate.
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from src.controllers.chatbot_controller import ChatbotController, get_default_chatbot_controller
from src.api.schemas import SendMessageResponse, SendMessageRequest, UpdateModelRequest, UpdateModelResponse
from src.config.settings import settings

router = APIRouter(tags=["Colgate Chatbot"])


@router.post("/send-message", response_model=SendMessageResponse)
async def send_message(
    message_request: SendMessageRequest = Body(...),
    chatbot_controller: ChatbotController = Depends(get_default_chatbot_controller),
):
    """
    Endpoint para enviar un mensaje al agente de Colgate.

    Args:
        message_request (SendMessageRequest): Datos del mensaje a enviar.
        chatbot_controller (ChatbotController): Controlador del chatbot inyectado.

    Returns:
        send_message_response (SendMessageResponse): Respuesta generada por el agente.
    """
    try:
        output_message = chatbot_controller.send_message(
            messages=[{"role": "user", "content": message_request.message}],
            thread_id=message_request.cellphone,
        )
        return SendMessageResponse(output=output_message)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al usar el agente de Colgate: {str(e)}"
        )


@router.put("/update-model", response_model=UpdateModelResponse)
async def update_model(
    update_request: UpdateModelRequest = Body(...),
    chatbot_controller: ChatbotController = Depends(get_default_chatbot_controller),
):
    """
    Endpoint para actualizar la configuración del modelo del chatbot.
    Requiere API key válida para autenticación.

    Args:
        update_request (UpdateModelRequest): Datos de actualización incluyendo API key.
        chatbot_controller (ChatbotController): Controlador del chatbot inyectado.

    Returns:
        UpdateModelResponse: Confirmación de la actualización.

    Raises:
        HTTPException: Si la API key es inválida o hay error en la actualización.
    """
    # Validar API key
    if update_request.api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="API key inválida. No autorizado para actualizar la configuración."
        )

    # Validar que al menos un parámetro esté presente
    if update_request.temperature is None and update_request.max_tokens is None:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar al menos un parámetro para actualizar (temperature o max_tokens)"
        )

    try:
        # Actualizar configuración del modelo
        chatbot_controller.update_model_config(
            temperature=update_request.temperature,
            max_tokens=update_request.max_tokens
        )

        return UpdateModelResponse(
            message="Configuración del modelo actualizada exitosamente",
            temperature=update_request.temperature,
            max_tokens=update_request.max_tokens
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=f"Parámetros inválidos: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar la configuración del modelo: {str(e)}"
        )
