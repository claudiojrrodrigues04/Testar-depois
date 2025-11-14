# app/models/employee.py
import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, func, ForeignKey
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    
    # --- Chaves Estrangeiras ---
    
    # Aponta para o ID da tabela 'departments'
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    
    # Aponta para o ID da tabela 'roles'
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    # --- Relacionamentos (para facilitar a consulta) ---
    
    # Permite acessar os dados do departamento (ex: employee.department.name)
    department: Mapped["Department"] = relationship(back_populates="employees")
    
    # Permite acessar os dados do cargo (ex: employee.role.title)
    role: Mapped["Role"] = relationship(back_populates="employees")

    # Datas de criação/alteração
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )