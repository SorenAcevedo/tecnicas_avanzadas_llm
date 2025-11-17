"""
Rutas API relacionadas con el LLM de Colgate.
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from src.controllers.chatbot_controller import ChatbotController, get_default_chatbot_controller
from src.api.schemas import SendMessageResponse, SendMessageRequest

router = APIRouter()


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
