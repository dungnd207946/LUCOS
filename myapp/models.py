from flask_login            import UserMixin
from sqlalchemy             import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm         import relationship
from myapp.templates.config import db
from myapp                  import app
from datetime               import datetime
#import pandas as pd

class Khach_hang(db.Model):
    __tablename__      = 'khach_hang'
    id                 = Column(String(50), primary_key=True, nullable=False, unique=True, default='0')
    ten_khach_hang     = Column(String(200), nullable=False)
    so_dien_thoai      = Column(String(20))
    email              = Column(String(50))
    khu_vuc            = Column(String(20))
    dia_chi            = Column(String(200))
    nhom_khach_hang    = Column(String(50))
    ngay_sinh          = Column(String(20))
    skin_property      = Column(Integer)
    payment_ability    = Column(String(20))
    last_buying_day    = Column(String(50))
    point              = Column(Integer)
    active             = Column(Boolean)
    day_without_buying = Column(Integer)
    picture            = Column(String(200))
    is_experience      = Column(Boolean)
    gender             = Column(String(50))
    profile_image      = Column(String(200))
    note               = Column(String(200))    
    # Đây là thuộc tính được SQLAlchemy tự động xử lý,
    # nó không phải là một cột trong bảng cơ sở dữ liệu. Đây là một collection của các đối tượng san_pham
    don_hangs          = relationship('Don_hang', secondary='kh_dh',back_populates='khach_hangs' , lazy=True)
    skin_types         = relationship('Skin_type', secondary='customer_skin', back_populates='customers', lazy=True)

class KH_DH(db.Model): #khach hang - don hang
    __tablename__      = 'kh_dh'
    khach_hang_id      = Column(String(50), ForeignKey('khach_hang.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    don_hang_id        = Column(String(20), ForeignKey('don_hang.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)

class Don_hang(db.Model):
    __tablename__      = 'don_hang'
    id                 = Column(String(50), primary_key=True, nullable=False)
    document_date      = Column(String(50))
    finish_date        = Column(String(50))
    branch             = Column(String(200))
    selling_source     = Column(String(50))
    staff              = Column(String(50))
    customer_name      = Column(String(200))
    product_amount     = Column(Integer)
    total_price        = Column(Integer)
    customer_payment   = Column(Integer)
    note               = Column(String(100))
    # relationship
    khach_hangs        = relationship('Khach_hang', secondary='kh_dh', back_populates='don_hangs', lazy=True)
    san_phams          = relationship('San_pham', secondary='dh_sp', back_populates='don_hangs', lazy=True)


class DH_SP(db.Model): #khach hang - san pham
    __tablename__      = 'dh_sp'
    don_hang_id        = Column(String(20), ForeignKey('don_hang.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    san_pham_id        = Column(Integer, ForeignKey('san_pham.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    so_luong           = Column(Integer, nullable=False)
class San_pham(db.Model):
    __tablename__      = 'san_pham'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    ten_san_pham       = Column(String(200), nullable=False)
    listed_price       = Column(Integer)
    mo_ta              = Column(String(50))
    anh                = Column(String(200))
    ma_SKU             = Column(String(50))
    khoi_luong         = Column(String(50))
    outdate_days       = Column(Integer)
    amount             = Column(Integer)

    # relationship
    don_hangs  = relationship('Don_hang', secondary='dh_sp', back_populates='san_phams', lazy=True)
    skin_types = relationship('Skin_type', secondary='product_skin', back_populates='products', lazy=True)
    def __str__(self):
        return self.ten_san_pham

class DonHangChiTiet(db.Model):
    __tablename__      = 'don_hang_chi_tiet'
    stt                = Column(Integer, primary_key=True, nullable=False)
    don_hang_id        = Column(String(50))
    ten_san_pham       = Column(String(200))
    so_luong           = Column(Integer)


class Skin_type(db.Model):
    __tablename__      = 'skin_type'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type_name          = Column(String(100))
    #relationship
    products           = relationship('San_pham', secondary='product_skin', back_populates='skin_types', lazy=True)
    customers          = relationship('Khach_hang', secondary='customer_skin', back_populates='skin_types', lazy=True)

class Product_skin(db.Model):
    __tablename__      = 'product_skin'
    skin_type_id       = Column(Integer, ForeignKey('skin_type.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    product_id         = Column(Integer, ForeignKey('san_pham.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)

class Customer_skin(db.Model):
    __tablename__      = 'customer_skin'
    skin_type_id       = Column(Integer, ForeignKey('skin_type.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    customer_id        = Column(String(50), ForeignKey('khach_hang.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)

class Task(db.Model):
    __tablename__      = 'task'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    description        = Column(String(500))

class Task_Customer(db.Model):
    __tablename__      = 'task_customer'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    task_id            = Column(Integer, ForeignKey('task.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    customer_id        = Column(String(50), ForeignKey('khach_hang.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    staff_id           = Column(Integer, ForeignKey('user_account.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    deadline           = Column(String(50))
    finished           = Column(Boolean)
    priority           = Column(Integer)
    note               = Column(String(500))
    outdated           = Column(Boolean)
    extra_description  = Column(String(500))
    #relationship
    staff              = relationship("User_account", foreign_keys=[staff_id])
    task               = relationship("Task", foreign_keys=[task_id])
    customer           = relationship("Khach_hang", foreign_keys=[customer_id])
class User_account(db.Model, UserMixin):
    __tablename__      = 'user_account'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    full_name          = Column(String(50), nullable=False)
    username           = Column(String(50), nullable=False, unique=True)
    phone_number       = Column(String(20), nullable=False)
    user_password      = Column(String(50), nullable=False)
    user_role          = Column(String(20))

    #relationship
    cards              = relationship("SpaCard", secondary='card_staff', back_populates='staffs', lazy=True)

class Treatment(db.Model):
    __tablename__      = 'treatment'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name               = Column(String(50), nullable=False)
    description        = Column(String(200))
    price              = Column(Integer)
    duration           = Column(Integer)
    tour_price         = Column(Integer)

    #relationship
    cards              = relationship("SpaCard", secondary='card_treatment', back_populates='treatments', lazy=True)
class Card_Treatment(db.Model):
    __tablename__      = 'card_treatment'
    card_id            = Column(Integer, ForeignKey('spa_card.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    treatment_id       = Column(Integer, ForeignKey('treatment.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    price              = Column(Integer)
    total_time         = Column(Integer)
    time_used          = Column(Integer)


class SpaCard(db.Model):
    __tablename__      = 'spa_card'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    customer_id        = Column(String(50), ForeignKey('khach_hang.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    total_price        = Column(Integer)
    paid               = Column(Integer)
    debt               = Column(Integer, nullable=False)
    note               = Column(String(500))
    date               = Column(String(50), default=lambda: datetime.now().strftime('%d/%m/%Y %H:%M'))

    # relationship
    customer           = relationship("Khach_hang", foreign_keys=[customer_id])
    treatments         = relationship("Treatment", secondary='card_treatment', back_populates='cards', lazy=True)
    staffs             = relationship("User_account", secondary='card_staff', back_populates='cards', lazy=True)
class Mask(db.Model):
    __tablename__      = 'mask'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    mask_name          = Column(String(50), nullable=False)
class SpaBooking(db.Model):
    __tablename__      = 'spa_booking'
    id                 = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    card_id            = Column(Integer, ForeignKey('spa_card.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    treatment_id       = Column(Integer, ForeignKey('treatment.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    staff_id           = Column(Integer, ForeignKey('user_account.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    mask_id            = Column(Integer, ForeignKey('mask.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    date               = Column(String(50))
    note               = Column(String(200))
    customer_demand    = Column(String(200))
    status             = Column(Integer) # quy ước 1 là Chưa đến, 2 là Hoàn thành, 3 là Hủy
    staff_money        = Column(Integer)
    is_new_customer    = Column(Boolean)
    is_single_book     = Column(Boolean)

    # relationship
    spa_card           = relationship("SpaCard", foreign_keys=[card_id])
    treatment          = relationship("Treatment", foreign_keys=[treatment_id])
    staffs             = relationship("User_account", foreign_keys=[staff_id])
    masks              = relationship("Mask", foreign_keys=[mask_id])

class Card_Staff(db.Model):
    __tablename__      = 'card_staff'
    card_id            = Column(Integer, ForeignKey('spa_card.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    staff_id           = Column(Integer, ForeignKey('user_account.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    divide_money       = Column(Float)

if __name__ == "__main__":
    app.app_context().push()
    db.create_all()

