# app/routers/auth.py

# Importações principais
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

# ORM e utilitários
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path

# Nossos modelos e utilitários de autenticação
from app.database import get_db, engine, Base
from app.models import User
from app.auth_utils import hash_password, verify_password

# Cria o roteador de autenticação
router = APIRouter(
    tags=["Authentication"] # Tag para a documentação
)

# Cria as tabelas do banco (assegura que a tabela 'users' seja criada)
Base.metadata.create_all(bind=engine)

# Configuração de diretório de templates
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ------------------------------------------------------------------
# 1. PÁGINA DE CADASTRO (GET)
# Rota: GET /register
# ------------------------------------------------------------------
@router.get("/register")
def register_form(request: Request):
    # Se o usuário já estiver logado, manda ele para a home
    if request.session.get("user_id"):
        return RedirectResponse(url="/employees", status_code=status.HTTP_303_SEE_OTHER)
        
    # Apenas mostra o formulário de cadastro
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )

# ------------------------------------------------------------------
# 2. PROCESSAR CADASTRO (POST)
# Rota: POST /register
# ------------------------------------------------------------------
@router.post("/register")
def process_register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Validação 1: Senhas não batem
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "As senhas não conferem."}
        )
    
    # Validação 2: Email já existe
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Este email já está cadastrado."}
        )

    # Criptografa a senha antes de salvar
    hashed_pass = hash_password(password)
    
    # Cria o usuário
    new_user = User(email=email, hashed_password=hashed_pass)
    db.add(new_user)
    db.commit()

    # Redireciona para a página de login com mensagem de sucesso
    return RedirectResponse(url="/login?msg=success", status_code=status.HTTP_303_SEE_OTHER)


# ------------------------------------------------------------------
# 3. PÁGINA DE LOGIN (GET)
# Rota: GET /login
# ------------------------------------------------------------------
@router.get("/login")
def login_form(request: Request, msg: str | None = None):
    # Se o usuário já estiver logado, redireciona para a home
    if request.session.get("user_id"):
        return RedirectResponse(url="/employees", status_code=status.HTTP_303_SEE_OTHER)

    context = {"request": request}
    if msg == "success":
        context["success"] = "Usuário cadastrado com sucesso! Faça o login."
    
    return templates.TemplateResponse(
        "auth/login.html",
        context
    )

# ------------------------------------------------------------------
# 4. PROCESSAR LOGIN (POST)
# Rota: POST /login
# ------------------------------------------------------------------
@router.post("/login")
def process_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Busca o usuário pelo email
    user = db.scalar(select(User).where(User.email == email))
    
    # Validação 1: Usuário não existe
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Email ou senha inválidos."}
        )
    
    # Validação 2: Senha incorreta
    if not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Email ou senha inválidos."}
        )

    # --- SUCESSO ---
    # Armazena os dados do usuário na sessão (cookie)
    # Guardamos apenas o ID e o Email para referência
    request.session["user_id"] = user.id
    request.session["user_email"] = user.email

    # Redireciona para a página principal do app (ex: funcionários)
    return RedirectResponse(url="/employees", status_code=status.HTTP_303_SEE_OTHER)


# ------------------------------------------------------------------
# 5. LOGOUT
# Rota: GET /logout
# ------------------------------------------------------------------
@router.get("/logout")
def logout(request: Request):
    # Limpa a sessão
    request.session.clear()
    # Redireciona para a página de login
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)