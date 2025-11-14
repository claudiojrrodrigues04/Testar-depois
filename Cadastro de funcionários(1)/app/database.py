# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# ------------------------------------------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS
# ------------------------------------------------------------------

# 1. Define o "endereço" do banco.
# Vamos usar o SQLite, que é um banco de dados simples baseado em arquivo.
# Ele vai criar um arquivo chamado 'app.db' na raiz do seu projeto.
DATABASE_URL = "sqlite:///./app.db"

# 2. Cria o "motor" (engine) do SQLAlchemy.
# O 'connect_args' é específico para o SQLite,
# permitindo que ele seja usado em aplicações web (com 'threads').
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 3. Cria a "fábrica" de sessões.
# Uma sessão é a forma como interagimos (consultamos, inserimos, etc.)
# com o banco de dados.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 4. Cria a Classe 'Base' Declarativa.
# Todos os seus arquivos de Model (User, Product, Employee)
# vão "herdar" desta classe para se tornarem tabelas.
class Base(DeclarativeBase):
    pass


# ------------------------------------------------------------------
# DEPENDÊNCIA DO FASTAPI
# ------------------------------------------------------------------

def get_db():
    """
    Esta é uma "Dependência" do FastAPI.
    Ela garante que:
    1. Uma sessão com o banco seja aberta quando a rota começar.
    2. A sessão seja fechada quando a rota terminar (mesmo se der erro).
    
    Usamos isso em todas as rotas que precisam falar com o banco:
    ... def minha_rota(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()