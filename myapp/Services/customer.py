from sqlalchemy import func
from datetime import datetime
from myapp.models import Khach_hang, Task_Customer, Task, Don_hang, KH_DH, San_pham, DH_SP, SpaCard, Skin_type
from myapp.templates.config import db


def getAllCustomers():
    return Khach_hang.query.filter(Khach_hang.active == True).all()
def get_customer_having_task():
    customer = Khach_hang.query.filter(Khach_hang.id == Task_Customer.customer_id)
    return customer

def get_order(khach_hang_id):
    orders = Don_hang.query.filter(Don_hang.id == KH_DH.don_hang_id, KH_DH.khach_hang_id == khach_hang_id)
    product_by_order = {}
    amount_product_per_order = {}
    for order in orders:
        product_by_order[order.id] = San_pham.query.filter(San_pham.id == DH_SP.san_pham_id,
                                                           DH_SP.don_hang_id == order.id)
        # Mark product follow by the order id.
        amount_product_per_order[order.id] = {}
        for product in product_by_order[order.id]:
            amount_product_per_order[order.id][product.id] = DH_SP.query.filter(DH_SP.don_hang_id == order.id,
                                                                                DH_SP.san_pham_id == product.id)
            # Mark the amount of product in each order by both order id and product id.

    return orders, product_by_order, amount_product_per_order

def get_detail_customer(khach_hang_id):
    result = (db.session.query(Khach_hang.id, Khach_hang.ten_khach_hang, Khach_hang.gender, Khach_hang.so_dien_thoai, Khach_hang.email, Khach_hang.khu_vuc, Khach_hang.dia_chi, Khach_hang.ngay_sinh, Khach_hang.payment_ability, Khach_hang.profile_image, Khach_hang.note, Skin_type.type_name)
              .outerjoin(Skin_type, Khach_hang.skin_property == Skin_type.id)
              .filter(Khach_hang.id == khach_hang_id)
              .all())
    return result


def getCustomerByCard(card_id):
    return db.session.query(SpaCard.id, Khach_hang.ten_khach_hang).join(Khach_hang, SpaCard.customer_id == Khach_hang.id).filter(SpaCard.id == card_id).first()

def getGroupCustomerList():
    source_data = getAllCustomers()
    nhom_kh_list = []
    for user in source_data:
        if user.nhom_khach_hang and user.nhom_khach_hang not in nhom_kh_list and user.nhom_khach_hang is not None:
            nhom_kh_list.append(user.nhom_khach_hang)
    nhom_kh_list_sorted = sorted(nhom_kh_list)
    return nhom_kh_list_sorted

def getAreaCustomerList():
    source_data = getAllCustomers()
    khu_vuc_list = []
    for user in source_data:
        if user.khu_vuc and user.khu_vuc not in khu_vuc_list and user.khu_vuc is not None:
            khu_vuc_list.append(user.khu_vuc)
    khu_vuc_list_sorted = sorted(khu_vuc_list)
    return khu_vuc_list_sorted

def getSpaCustome():
    return []
def onlySpaCustomer():
    return (db.session.query(Khach_hang.id.label('customer_id') , Khach_hang.ten_khach_hang.label('customer_name'))
        .join(SpaCard, Khach_hang.id == SpaCard.customer_id)
        .group_by(Khach_hang.id, Khach_hang.ten_khach_hang)
        .having(func.count(SpaCard.id) >= 1)
        )

def format_date_for_input(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return "Wrong Value"