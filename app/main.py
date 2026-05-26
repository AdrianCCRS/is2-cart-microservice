from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.redis_client import connect_redis, disconnect_redis, get_redis
from app.controllers.cart_controller import router as cart_router

app = FastAPI(title="Cart Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(LookupError)
async def lookup_error_handler(request: Request, exc: LookupError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


app.include_router(cart_router)


@app.on_event("startup")
async def startup():
    await connect_redis()


@app.on_event("shutdown")
async def shutdown():
    await disconnect_redis()


@app.get("/health")
async def health_check():
    redis = get_redis()
    redis_status = "error"
    redis_detail = None
    try:
        if redis is None:
            redis_detail = "client not initialized"
        else:
            await redis.ping()
            redis_status = "ok"
    except Exception as e:
        redis_detail = str(e)
    overall = "ok" if redis_status == "ok" else "degraded"
    return {
        "status": overall,
        "redis": redis_status,
        "detail": redis_detail,
    }
