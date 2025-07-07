from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.events.startup import events as startup_event
from src.routers.User.view import User_router
from src.routers.Admin.views import admin_router
from src.routers.Chatbox.views import chatbox_router
from src.routers.websocket.chatbox.views import websocket_chatbox
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


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
    print(exc.detail)
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
app.include_router(admin_router)
app.include_router(chatbox_router)
app.include_router(websocket_chatbox)


def entry_page_html():
    with open("./src/entry_page.html", "r", encoding="utf-8") as f:
        html_template = f.read()
    return HTMLResponse(content=html_template, status_code=200)

def ws_guide_html():
    with open("./src/ws_guide.html", "r", encoding="utf-8") as f:
        html_template = f.read()
    return HTMLResponse(content=html_template, status_code=200)

@app.get("/ws-docs", response_class=HTMLResponse)
async def ws_docs_page(request : Request):
    return ws_guide_html()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return entry_page_html()

