# main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

# Importa os roteadores que já temos
from app.routers.products import router as products_router
from app.routers.departments import router as departments_router
from app.routers.roles import router as roles_router
from app.routers.employees import router as employees_router

# NOVO: Importa o roteador de autenticação
from app.routers.auth import router as auth_router


app = FastAPI(title="Projeto")

# Adiciona o Middleware de Sessão
app.add_middleware(
    SessionMiddleware, 
    secret_key="SECRET_KEY_MUITO_SECRETA",
    https_only=False,
    max_age=1800
)

# Inclui todas as suas rotas
app.include_router(products_router)
app.include_router(departments_router)
app.include_router(roles_router)
app.include_router(employees_router)

# NOVO: Inclui as rotas de autenticação (login, logout, register)
app.include_router(auth_router)


# Arquivos estáticos (CSS, imagens, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Status/saúde do servidor (com host/porta)
@app.get("/status")
def status(request: Request):
    return {
        "status": "ok",
        "host": request.client.host,
        "port": request.url.port or 80,
        "scheme": request.url.scheme,
        "path": request.url.path,
    }