from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from model.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # کاربری که این عملیات را انجام داده
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # بخش سیستم
    # فعلاً panel است؛ بعداً system را هم اضافه می‌کنیم
    section = Column(String(20), nullable=False, default="panel", index=True)

    # نوع عملیات
    # مثال: LOGIN, LOGOUT, CREATE, UPDATE, DELETE, CHANGE_ROLE
    action = Column(String(50), nullable=False, index=True)

    # موجودیتی که عملیات روی آن انجام شده
    # مثال: user, bank, account, car, home
    entity = Column(String(50), nullable=True)

    # ID موجودیت
    entity_id = Column(Integer, nullable=True)

    # توضیح عملیات
    description = Column(Text, nullable=True)

    # IP کاربر
    ip_address = Column(String(45), nullable=True, index=True)

    # زمان انجام عملیات
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )