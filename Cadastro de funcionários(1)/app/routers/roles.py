# app/routers/roles.py

# Importações principais do FastAPI
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

# ORM e utilitários de banco de dados
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path

# Importações do projeto
from app.database import get_db, engine, Base
# Importa o novo Model que criamos
from app.models import Role # <-- Mudamos para Role

# Cria o roteador de cargos
# 'prefix="/roles"' significa que todas as rotas aqui começarão com /roles
router = APIRouter(
    prefix="/roles",
    tags=["Roles"] # <-- Tag para documentação
)

# Cria as tabelas do banco
Base.metadata.create_all(bind=engine)

# Configuração de diretório de templates
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ------------------------------------------------------------------
# 1. LISTAR CARGOS (GET)
# Rota: GET /roles/
# ------------------------------------------------------------------
@router.get("/")
def list_roles(request: Request, db: Session = Depends(get_db)):
    # Busca todos os cargos, ordenando pelo título
    roles = db.scalars(select(Role).order_by(Role.title)).all()
    
    # Renderiza a página de listagem
    # Vamos precisar criar este arquivo HTML
    return templates.TemplateResponse(
        "roles/index.html", # <-- Novo HTML
        {"request": request, "roles": roles}
    )

# ------------------------------------------------------------------
# 2. FORMULÁRIO DE NOVO CARGO (GET)
# Rota: GET /roles/new
# ------------------------------------------------------------------
@router.get("/new")
def new_role_form(request: Request):
    # Apenas exibe o formulário de cadastro
    # Vamos precisar criar este arquivo HTML
    return templates.TemplateResponse(
        "roles/new.html", # <-- Novo HTML
        {"request": request}
    )

# ------------------------------------------------------------------
# 3. CRIAÇÃO DE CARGO (POST)
# Rota: POST /roles/
# ------------------------------------------------------------------
@router.post("/")
def create_role(
    request: Request,
    title: str = Form(...),  # <-- Mudamos de 'name' para 'title'
    db: Session = Depends(get_db),
):
    # Validação: Verifica se o campo não está vazio
    if not title.strip():
        # Se estiver vazio, recarrega o formulário com uma mensagem de erro
        return templates.TemplateResponse(
            "roles/new.html",
            {"request": request, "error": "O título é obrigatório"}
        )

    # Validação: Verifica se o cargo já existe
    existing = db.scalar(select(Role).where(Role.title == title.strip()))
    if existing:
        # Se já existir, recarreGao formulário com uma mensagem de erro
        return templates.TemplateResponse(
            "roles/new.html",
            {"request": request, "error": "Este cargo já existe"}
        )

    # Cria o objeto e salva no banco
    db.add(Role(title=title.strip()))
    db.commit()

    # Redireciona para a listagem de cargos
    return RedirectResponse(url="/roles", status_code=status.HTTP_303_SEE_OTHER)