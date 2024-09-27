from sqlalchemy import func, and_
from myapp.models import User_account, SpaBooking
from myapp.templates.config import db
from datetime import datetime

def getStaffReport(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    query = db.session.query(
        User_account.full_name.label('staff_name'),
        func.count(func.if_(SpaBooking.is_new_customer == True, 1, None)).label('new_customers_count'),  # Đếm khách mới
        func.count(SpaBooking.id).label('completed_bookings_count'), #Đếm booking
        func.sum(SpaBooking.staff_money).label('total_staff_money')  # Tổng tiền của staff
    ).join(User_account, SpaBooking.staff_id == User_account.id
    # Đếm booking hoàn thành (status = 2)
    ).filter(SpaBooking.status == 2
    ).filter(User_account.user_role == 'USER',  # Lọc user có role là 'USER'
             and_(
                 func.str_to_date(SpaBooking.date, '%d/%m/%Y %H:%i') >= start_date,  # So sánh thời gian bắt đầu
                 func.str_to_date(SpaBooking.date, '%d/%m/%Y %H:%i') <= end_date)
    ).group_by(User_account.full_name).all()  # Nhóm theo tên nhân viên
    return query
