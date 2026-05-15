from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.cart_service import CartService
from app.security import verify_api_key

router = APIRouter( prefix="/api/cart", 
                    tags=["cart"] ,
                    dependencies=[Depends(verify_api_key)])
cart_service = CartService()


class AddItemRequest(BaseModel):
    product_id: str
    quantity: int


@router.post("/{user_id}/items", status_code=201)
async def add_item_to_cart(user_id: str, body: AddItemRequest):
    try:
        result = await cart_service.add_item(user_id, body.product_id, body.quantity)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{user_id}/ttl")
async def get_cart_ttl(user_id: str):
    try:
        result = await cart_service.get_ttl(user_id)
        return result
    except (ValueError, LookupError):
        raise  # Capturado por los handlers centralizados de main.py
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{user_id}")
async def get_cart(user_id: str):
    try:
        result = await cart_service.get_cart(user_id)
        return result
    except ValueError:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/{user_id}/items/{item_id}")
async def delete_item(user_id: str, item_id: str):
    try:
        result = await cart_service.remove_item(user_id, item_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


class UpdateItemRequest(BaseModel):
    quantity: int


@router.put("/{user_id}/items/{item_id}")
async def update_item(user_id: str, item_id: str, body: UpdateItemRequest):
    try:
        result = await cart_service.update_item(user_id, item_id, body.quantity)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")



@router.delete("/{user_id}")
async def clear_cart(user_id: str):
    try:
        result = await cart_service.clear_cart(user_id)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")