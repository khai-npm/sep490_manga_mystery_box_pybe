from fastapi import FastAPI, HTTPException, Request
# from src.routers.products.views import product_router
# from src.routers.orders.views import order_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.events.startup import events as startup_event
# from src.routers.account.views import account_router
# from src.routers.task.views import task_router
# from src.routers.admin.views import admin_router
from src.routers.User.view import User_router


app = FastAPI(on_startup=startup_event)



origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(order_router)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        # content={"detail": exc.detail, "code": exc.status_code},
        content={
                "success": False,
                "data": None,
                "length":  0,
                "error": exc.detail,
                "error_code": exc.status_code
        }
    )

app.include_router(User_router)

# app.include_router(account_router)
# app.include_router(task_router)
# app.include_router(admin_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}