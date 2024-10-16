from sqlalchemy import func, and_, case
from myapp.models import User_account, SpaBooking, Mask, SpaCard, Card_Staff, Khach_hang
from myapp.templates.config import db
from datetime               import datetime

def getStaffReport(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    query = db.session.query(
        User_account.id.label('staff_id'),
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
    ).group_by(User_account.id).all()  # Nhóm theo tên nhân viên
    return query

def countMaskFromBooking(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    query = (db.session.query(
        Mask.id.label('mask_id'),
        Mask.mask_name,
        func.count(Mask.id).label('mask_quantity'),
        )
    .join(SpaBooking, Mask.id == SpaBooking.mask_id)
    .filter(func.str_to_date(SpaBooking.date, '%d/%m/%Y %H:%i') >= start_date, func.str_to_date(SpaBooking.date, '%d/%m/%Y %H:%i') <= end_date)
    .group_by(Mask.id).all())

    return query

def getRevenueByStaff(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    query = (db.session.query(
        User_account.id.label('staff_id'),
        User_account.full_name.label('staff_name'),
        func.sum(
            case(
                (Khach_hang.is_experience != True, SpaCard.paid), # Lấy doanh thu từ khách mua thẻ
                else_=0
            )
        ).label('card_revenue'),
        func.sum(
            case(
                (Khach_hang.is_experience == True, SpaCard.paid), #Lấy doanh thu khách trải nghiệm 1 buổi
                else_=0
            )
        ).label('experience_revenue'),
        (
            func.sum(
                case(
                    (Khach_hang.is_experience != True, SpaCard.paid),
                    else_=0
                )
            ) +
            func.sum(
                case(
                    (Khach_hang.is_experience == True, SpaCard.paid),
                    else_=0
                )
            )
        ).label('total_revenue')
    )
    .join(Card_Staff, User_account.id == Card_Staff.staff_id)
    .join(SpaCard, Card_Staff.card_id == SpaCard.id)
    .join(Khach_hang, SpaCard.customer_id == Khach_hang.id)
    .filter(User_account.user_role == 'USER',
            and_(
                func.str_to_date(SpaCard.date, '%d/%m/%Y %H:%i') >= start_date,  # So sánh thời gian bắt đầu
                func.str_to_date(SpaCard.date, '%d/%m/%Y %H:%i') <= end_date)
            )
    .filter(SpaCard.date != None)
    .group_by(User_account.id).all())

    return query

