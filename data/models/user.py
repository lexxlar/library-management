from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from data.database import Base
from core.security import check_password

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)  # librarian, admin, director
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    
    def check_password(self, password: str) -> bool:
        """Проверка пароля"""
        return check_password(password, self.password_hash)
    
    def has_permission(self, permission: str) -> bool:
        """Проверка прав доступа"""
        permissions = {
            'admin': ['all'],
            'librarian': ['view', 'loan', 'return', 'register_reader'],
            'director': ['view', 'reports']
        }
        user_permissions = permissions.get(self.role, [])
        return 'all' in user_permissions or permission in user_permissions
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"