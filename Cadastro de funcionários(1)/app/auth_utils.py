# app/auth_utils.py
from passlib.context import CryptContext

# Define o "contexto" de criptografia, dizendo que vamos usar o 'bcrypt'
# Este é o padrão de mercado para hashear senhas.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro bate com o hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)