from flask import Blueprint, url_for, request, render_template, flash, redirect, jsonify, session
from flask_login import login_required, current_user
from sqlalchemy import desc, and_
from flask_sqlalchemy import pagination
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from myapp.models import Khach_hang, Task_Customer, User_account, SpaCard, Treatment, SpaBooking, Card_Treatment, Mask, Card_Staff, Skin_type, Customer_skin
from myapp.API.services import delete, load_customer, update_day_without_buying
from myapp.Services.task import getTaskByCustomerID_StaffID, get_table_task_for_admin, getALlTask, get_table_task_for_only_staff, check_task_outdated
from myapp.Services.customer import get_order, get_detail_customer, getAllCustomers, getCustomerByCard, getGroupCustomerList, getAreaCustomerList, onlySpaCustomer
from myapp.Services.user import getStaff
from myapp.Services.spa import getAllCard, getCardByCustomerID, getTreatmentByCardID, getTreatmentByID, getBookingByCardID, getSpaCardCustomer
from myapp.templates.config import db
from myapp.auth import admin_required, dev_required, prevent_guest
from datetime import datetime

api = Blueprint('api', __name__, static_folder='static', template_folder='templates')

@api.route('/customer-filter', methods=['POST'])
@login_required
def customer_filter(): #Đang xảy ra lỗi: Chuyển trang chưa kết hợp được với bộ lọc
    per_page            = 20
    page                = request.args.get('page', 1, type=int)
    kw                  = request.args.get('search')
    kw                  = kw if kw else ""
    khach_hang          = load_customer(kw=kw)
    source_data         = getAllCustomers() # Source data dùng để lấy dữ liệu vào ô lọc
    nhom_kh_list_sorted = getGroupCustomerList()
    khu_vuc_list_sorted = getAreaCustomerList()
    if request.method == 'POST':
        nhom_khach_hang          = request.form['nhom_khach_hang']
        khu_vuc                  = request.form['khu_vuc']
        conditions               = []
        selected_nhom_khach_hang = nhom_khach_hang
        selected_khu_vuc         = khu_vuc
        if nhom_khach_hang != '':
            conditions.append(Khach_hang.nhom_khach_hang == nhom_khach_hang)
        if khu_vuc != '':
            conditions.append(Khach_hang.khu_vuc == khu_vuc)

        filtered_query = Khach_hang.query.filter(and_(*conditions))
        filtered = filtered_query.paginate(page=page, per_page=per_page, error_out=False)
        # khach_hang_filtered = filtered.items
        total_customers = len(filtered_query.all())
        print(total_customers)
        return render_template('customer/infor-customer.html',
                               khach_hang               = filtered_query,
                               source_data              = source_data,
                               nhom_kh_list_sorted      = nhom_kh_list_sorted,
                               khu_vuc_list_sorted      = khu_vuc_list_sorted,
                               kw='',
                               selected_nhom_khach_hang = selected_nhom_khach_hang,
                               selected_khu_vuc         = selected_khu_vuc,
                               page                     = page,
                               total_customers          = total_customers)
