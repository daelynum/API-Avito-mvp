from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME, Float, Text, VARCHAR, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType
from sqlalchemy.sql import func
from database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(EmailType, unique=True)
    mobile_phone = Column(BigInteger, nullable=False, unique=True)
    town_id = Column(Integer, ForeignKey('towns.id'), nullable=False)
    password_hash = Column(VARCHAR(100), nullable=False)
    created_at = Column(DATETIME(timezone=True), server_default=func.now(), nullable=False)

    announcement = relationship('Announcements', lazy='joined', back_populates='user')
    favorite = relationship('Favorites', lazy='joined', back_populates='user')
    town = relationship('Towns', lazy='joined', back_populates='user')


class Towns(Base):
    __tablename__ = 'towns'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    town_name = Column(VARCHAR(100), nullable=False, unique=True)

    user = relationship('Users', lazy='joined', back_populates='town')
    announcement = relationship('Announcements', lazy='joined', back_populates='town')


class Announcements(Base):
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='cascade'), nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    text = Column(Text, nullable=False)
    town_id = Column(Integer, ForeignKey('towns.id'), nullable=False)
    created_at = Column(DATETIME(timezone=True), server_default=func.now(), nullable=False)

    user = relationship('Users', lazy='joined', back_populates='announcement')
    category = relationship('Categories', lazy='joined', back_populates='announcement')
    town = relationship('Towns', lazy='joined', back_populates='announcement')
    image = relationship('Images', lazy='joined', back_populates='announcement')
    favorite = relationship('Favorites', lazy='joined', back_populates='announcement')


class Images(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    announcement_id = Column(Integer, ForeignKey('announcements.id', ondelete='cascade'), nullable=False)
    data_path = Column(Text, nullable=False)

    announcement = relationship('Announcements', lazy='joined', back_populates='image')


class Favorites(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='cascade'), nullable=False)
    announcement_id = Column(Integer, ForeignKey('announcements.id', ondelete='cascade'), nullable=False, unique=True)
    created_at = Column(DATETIME(timezone=True), server_default=func.now(), nullable=False)

    user = relationship('Users', lazy='joined', back_populates='favorite')
    announcement = relationship('Announcements', lazy='joined', back_populates='favorite')


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_name = Column(VARCHAR(100), nullable=False, unique=True)

    announcement = relationship('Announcements', lazy='joined', back_populates='category')
