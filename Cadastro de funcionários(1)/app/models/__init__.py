# app/models/__init__.py

# Importa os modelos do nosso CRUD de funcionários
from .department import Department
from .role import Role
from .employee import Employee

# Importa o modelo de usuário (que fizemos)
from .user import User

# Importa o modelo original do professor
from .product import Product

# Exporta TODOS ELES
__all__ = [
    "Product", 
    "Department", 
    "Role", 
    "Employee", 
    "User"
]