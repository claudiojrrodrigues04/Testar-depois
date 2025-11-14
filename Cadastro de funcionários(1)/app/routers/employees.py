# app/routers/employees.py

# Importações principais do FastAPI
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

# ORM e utilitários de banco de dados
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from pathlib import Path

# Importações do projeto
from app.database import get_db, engine, Base
# !! Importamos os 3 modelos !!
from app.models import Employee, Department, Role 

# Cria o roteador de funcionários
router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

# Cria as tabelas do banco
Base.metadata.create_all(bind=engine)

# Configuração de diretório de templates
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ------------------------------------------------------------------
# 1. LISTAR FUNCIONÁRIOS (GET)
# Rota: GET /employees/
# ------------------------------------------------------------------
@router.get("/")
def list_employees(request: Request, db: Session = Depends(get_db)):
    # !! Consulta Otimizada !!
    # Usamos 'joinedload' para buscar os dados relacionados
    # (departamento e cargo) na MESMA consulta.
    # Isso evita múltiplas consultas ao banco (problema N+1).
    query = (
        select(Employee)
        .options(
            joinedload(Employee.department), 
            joinedload(Employee.role)
        )
        .order_by(Employee.name)
    )
    employees = db.scalars(query).all()
    
    # Renderiza a página de listagem
    return templates.TemplateResponse(
        "employees/index.html",
        {"request": request, "employees": employees}
    )

# ------------------------------------------------------------------
# 2. FORMULÁRIO DE NOVO FUNCIONÁRIO (GET)
# Rota: GET /employees/new
# ------------------------------------------------------------------
@router.get("/new")
def new_employee_form(request: Request, db: Session = Depends(get_db)):
    # !! Importante !!
    # Precisamos buscar todos os departamentos e cargos
    # para popular os <select> (dropdowns) no formulário.
    departments = db.scalars(select(Department).order_by(Department.name)).all()
    roles = db.scalars(select(Role).order_by(Role.title)).all()
    
    # Passamos os departamentos e cargos para o template
    return templates.TemplateResponse(
        "employees/new.html",
        {"request": request, "departments": departments, "roles": roles}
    )

# ------------------------------------------------------------------
# 3. CRIAÇÃO DE FUNCIONÁRIO (POST)
# Rota: POST /employees/
# ------------------------------------------------------------------
@router.post("/")
def create_employee(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    department_id: int = Form(...), # <-- Recebemos o ID do <select>
    role_id: int = Form(...),       # <-- Recebemos o ID do <select>
    db: Session = Depends(get_db),
):
    # Validação 1: Campos vazios
    if not name.strip() or not email.strip():
        error = "Nome e Email são obrigatórios."
    # Validação 2: Email duplicado
    elif db.scalar(select(Employee).where(Employee.email == email.strip())):
        error = "Este email já está cadastrado."
    else:
        error = None

    # Se houver erro de validação:
    if error:
        # !! Precisamos buscar departamentos e cargos NOVAMENTE !!
        # para re-renderizar o formulário com a mensagem de erro.
        departments = db.scalars(select(Department).order_by(Department.name)).all()
        roles = db.scalars(select(Role).order_by(Role.title)).all()
        
        return templates.TemplateResponse(
            "employees/new.html",
            {
                "request": request, 
                "departments": departments, 
                "roles": roles, 
                "error": error,
                # Devolve os valores que o usuário já digitou
                "form_data": {"name": name, "email": email, "department_id": department_id, "role_id": role_id}
            }
        )

    # Se passou na validação, cria o funcionário
    new_employee = Employee(
        name=name.strip(),
        email=email.strip(),
        department_id=department_id,
        role_id=role_id
    )
    db.add(new_employee)
    db.commit()

    # Redireciona para a listagem
    return RedirectResponse(url="/employees", status_code=status.HTTP_303_SEE_OTHER)