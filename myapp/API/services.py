import hashlib
from sqlalchemy import func, or_
from pymysql.cursors import DictCursor
from myapp.models import User_account, Khach_hang
from myapp.templates.config import db
from myapp.templates.config import mysql
from flask import jsonify, request, Flask
from flask_apscheduler import APScheduler
from datetime import datetime
from myapp import app

def add_user(full_name, username, user_password, **kwargs):
    user_password = str(hashlib.md5(user_password.encode('utf-8')).hexdigest())
    user = User_account(full_name     = full_name,
                        username     = username.strip(),
                        user_password= user_password.strip(),
                        phone_number = kwargs.get('phone_number'),
                        user_role    = kwargs.get('user_role'))
    db.session.add(user)
    db.session.commit()

def load_customer(kw = None):
    customers = Khach_hang.query.filter(Khach_hang.active.__eq__(True))
    print(kw)
    if kw:
        customers = customers.filter(or_(
                                     (func.lower(Khach_hang.id).contains(kw.lower())),
                                     (func.lower(Khach_hang.ten_khach_hang).contains(kw.lower())),
                                     (func.lower(Khach_hang.so_dien_thoai).contains(kw.lower())),
                                     (func.lower(Khach_hang.nhom_khach_hang).contains(kw.lower())),
                                     (func.lower(Khach_hang.khu_vuc).contains(kw.lower()))
                                     ))
    return customers

def get_user_by_id(user_id):
    return User_account.query.get(user_id)

def check_login(username, password):
    if username and password:
        user_password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
        return User_account.query.filter(User_account.username.__eq__(username),
                                        User_account.user_password.__eq__(user_password)).first()

def update(list, sqlQuery):
    try:
        data     = request.json
        bindData = [data.get(item, None) for item in list]
        if None in bindData:
            return jsonify({'message': 'Missing data'}), 400
        bindData = tuple(bindData)
        if request.method == 'PUT':
            conn                = mysql.connect()
            cursor              = conn.cursor(DictCursor)
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            respone             = jsonify('Update successfully!')
            respone.status_code = 200
            return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

def delete(sqlQuery, bindData):
    try:
        conn                = mysql.connect()
        cursor              = conn.cursor(DictCursor)
        cursor.execute(sqlQuery, bindData)
        conn.commit()
        respone             = jsonify('Delete successfully!')
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

#Thiết kế để mỗi lần khởi động app, hoặc nếu app chạy liên tục thì sau 1 ngày sẽ tự động gọi hàm update
def update_day_without_buying():
    customers = load_customer()
    for kh in customers:
        last_buying_days = kh.last_buying_day
        time_string = last_buying_days
        if time_string:
            start_time = datetime.strptime(time_string, "%d/%m/%Y %H:%M")
            current_time = datetime.now()
            delta = current_time - start_time
            days_difference = delta.days

            kh.day_without_buying = days_difference
        else:
            kh.day_without_buying = 9999
    db.session.commit()

