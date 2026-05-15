import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.logger import get_logger

"""
Módulo de seguridad del microservicio Cart.
Provee dos mecanismos de seguridad:
1. Autenticación por API Key mediante la cabecera HTTP X-API-Key.
   La clave esperada se configura con la variable de entorno API_KEY.
2. Validación del parámetro user_id para prevenir inyecciones y valores
   maliciosos en las rutas de los endpoints.
"""

logger = get_logger(__name__)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependencia de FastAPI que verifica la API Key en la cabecera X-API-Key.
    Lanza HTTP 401 si la clave es incorrecta o está ausente.
    La clave esperada se lee de la variable de entorno API_KEY.
    """
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        logger.warning("API_KEY env var not set - all requests will be rejected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key not configured on server"
        )
    if api_key != expected_key:
        logger.warning("Unauthorized request - invalid or missing API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key
