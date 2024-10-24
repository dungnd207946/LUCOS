from flask                   import Blueprint, url_for, request, render_template, flash, redirect, jsonify, session
from flask_login             import login_required, current_user
from sqlalchemy import desc, and_, func, case
from flask_sqlalchemy        import pagination
from sqlalchemy.exc          import SQLAlchemyError
from sqlalchemy.orm          import aliased
from myapp.models            import Khach_hang, Task_Customer, User_account, SpaCard, Treatment, SpaBooking, Card_Treatment, Mask, Card_Staff, Skin_type, Customer_skin
from myapp.API.services      import delete, load_customer, update_day_without_buying
from myapp.Services.task     import getTaskByCustomerID_StaffID, get_table_task_for_admin, getALlTask, get_table_task_for_only_staff, check_task_outdated
from myapp.Services.customer import get_order, get_detail_customer, getAllCustomers, getCustomerByCard, getGroupCustomerList, getAreaCustomerList, onlySpaCustomer
from myapp.Services.user     import getStaff
from myapp.Services.spa      import getAllCard, getCardByCustomerID, getTreatmentByCardID, getTreatmentByID, getBookingByCardID, getSpaCardCustomer, getAllTreatments, getAllBookingData, getCustomerCardDetail
from myapp.Services.report   import countMaskFromBooking, getRevenueByStaff
from myapp.templates.config  import db
from myapp.auth              import admin_required, dev_required, prevent_guest
from datetime                import datetime, timedelta

routes = Blueprint('routes', __name__, static_folder='static', template_folder='templates')

@routes.route('/')
def home_page():
    return render_template("HomePage.html")

@routes.context_processor  #Định nghĩa biến được dùng trong template
def common_response_1():
    infor_url = url_for('routes.infor_khach_hang')
    return {'infor_url': infor_url}

@routes.context_processor
def common_response_2():
    create_url = url_for('api.create_customer')
    return {'create_url': create_url}

@routes.context_processor
def common_response_3():
    task_url = url_for('routes.task')
    return {'task_url': task_url}

@routes.context_processor
def common_response_4():
    create_task_url = url_for('routes.create_task')
    return {'create_task_url': create_task_url}

@routes.context_processor
def common_response_5():
    infor_khach_hang_url = url_for('routes.infor_khach_hang')
    return {'infor_khach_hang_url': infor_khach_hang_url}

@routes.context_processor
def common_response_6():
    spa_url = url_for('routes.spa')
    return {'spa_url': spa_url}

@routes.context_processor
def common_response_7():
    create_card_url = url_for('routes.create_card')
    return {'create_card_url': create_card_url}

@routes.context_processor
def common_response_10():
    booking_url = url_for('routes.booking')
    return {'booking_url': booking_url}

@routes.route('/dash-board')
@login_required
def dash_board():
    return render_template("dashboard.html")

@routes.route('/khach-hang', methods=['GET'])
@login_required
def infor_khach_hang(): #Đang xảy ra lỗi: Chuyển trang chưa kết hợp được với bộ lọc
    per_page            = 20
    page                = request.args.get('page', 1, type=int)
    kw                  = request.args.get('search')
    kw                  = kw if kw else ""
    khach_hang          = load_customer(kw=kw)
    source_data         = getAllCustomers() # Source data dùng để lấy dữ liệu vào ô lọc
    nhom_kh_list_sorted = getGroupCustomerList()
    khu_vuc_list_sorted = getAreaCustomerList()

    pagination = khach_hang.paginate(page=page, per_page=per_page, error_out=False)

    khach_hang_filtered = pagination.items
    source_data = Khach_hang.query.all()
    total_customers = len(khach_hang.all())
    return render_template('customer/infor-customer.html',
                           khach_hang  = khach_hang,
                           source_data = source_data,
                           nhom_kh_list_sorted=nhom_kh_list_sorted,
                           khu_vuc_list_sorted=khu_vuc_list_sorted,
                           kw          = kw,
                           page        = page,
                           total_customers = total_customers)


@routes.route('/khach-hang/infor-khach-hang/<string:khach_hang_id>')
@login_required
def detail_khach_hang(khach_hang_id):
    detail                                             = get_detail_customer(khach_hang_id)
    orders, product_by_order, amount_product_per_order = get_order(khach_hang_id)

    return render_template('customer/detail-customer.html',
                           detail                      = detail,
                           orders                      = orders,
                           product_by_order            = product_by_order,
                           amount_product_per_order    = amount_product_per_order,
                           )

@routes.route('/khach-hang/them-khach-hang', methods=['GET'])
@login_required
def create_customer_view():
    skin = Skin_type.query.all()
    return render_template('customer/create-customer.html', skin=skin)

@routes.route('/khach-hang/infor-khach-hang/delete/<string:khach_hang_id>', methods=['DELETE'])
@login_required
@prevent_guest
def delete_khachhang_by_id(khach_hang_id):
    sqlQuery = 'DELETE FROM khach_hang WHERE id = %s'
    return delete(sqlQuery,khach_hang_id)

@routes.route('/khach-hang/update/<string:khach_hang_id>', methods=['GET'])
@login_required
def update_khach_hang_by_id(khach_hang_id):
    customers = Khach_hang.query.filter(Khach_hang.id == khach_hang_id)
    return render_template("customer/update-customer.html", detail=customers)

@routes.route('/get-spa-customer-suggestions') # Tìm kí tự trùng lặp giữa input và data rồi đưa ra kết quả
def get_spa_customer_suggestions():
    input_text = request.args.get('input')
    # Code để truy vấn dữ liệu từ cơ sở dữ liệu dựa trên input_text
    # Sau đó, trả về danh sách các gợi ý dưới dạng JSON
    if not input_text:
        return jsonify({'suggestions': []})
    customers = onlySpaCustomer()
    suggestions = [{'customer_id': customer.customer_id,
                    'name'       : customer.customer_name
                    }
                   for customer in customers]
    filtered_suggestions = [suggestion for suggestion in suggestions if input_text.lower() in suggestion['name'].lower() or input_text.lower() in str(suggestion['customer_id']).lower()]
    return jsonify({'suggestions': filtered_suggestions})


@routes.route('/get-all-spa-customer-suggestions')
def get_all_spa_customer_suggestions():
    customers = onlySpaCustomer()
    suggestions = [{'customer_id': customer.customer_id,
                    'name'       : customer.customer_name
                    }
                   for customer in customers]
    return jsonify({'suggestions': suggestions})

@routes.route('/get-customer-suggestions') # Tìm kí tự trùng lặp giữa input và data rồi đưa ra kết quả
def get_customer_suggestions():
    input_text = request.args.get('input')
    # Code để truy vấn dữ liệu từ cơ sở dữ liệu dựa trên input_text
    # Sau đó, trả về danh sách các gợi ý dưới dạng JSON
    if not input_text:
        return jsonify({'suggestions': []})

    customers = getAllCustomers()
    suggestions = [{'customer_id': customer.id,
                    'name'       : customer.ten_khach_hang,
                    'phone'      : customer.so_dien_thoai}
                   for customer in customers]
    suggestions = [suggestion for suggestion in suggestions if suggestion['name'] and suggestion['customer_id']]
    filtered_suggestions = [suggestion for suggestion in suggestions if input_text.lower() in suggestion['name'].lower() or input_text.lower() in suggestion['customer_id'].lower()]
    return jsonify({'suggestions': filtered_suggestions})

@routes.route('/get-all-customer-suggestions')
def get_all_customer_suggestions():
    customers = getAllCustomers()
    suggestions = [{'customer_id': customer.id,
                    'name'       : customer.ten_khach_hang,
                    'phone'      : customer.so_dien_thoai}
                   for customer in customers]
    return jsonify({'suggestions': suggestions})

@routes.route('/khach-hang/create-multi-task', methods=['GET'])
@login_required
def create_multi_task():
    allTask = getALlTask()
    allStaff = getStaff()
    return render_template("task/create_for_multi_customer.html", existing_tasks=allTask, staffs=allStaff)

@routes.route('/task', methods=['GET'])
@login_required
def task():
    update_day_without_buying()             # update số ngày chưa mua hàng mỗi khi gọi hàm
    check_task_outdated()
    if current_user.user_role == 'ADMIN':
        table = get_table_task_for_admin()
    else:
        table = get_table_task_for_only_staff()

    staffs = getStaff()
    staffs_ordered = staffs.order_by(User_account.full_name)
    return render_template("task/task.html", tables=table, staffs=staffs_ordered)

@routes.route('/task/task-detail/<string:khach_hang_id>/<string:staff_id>')
@login_required
def task_detail(khach_hang_id, staff_id):
    details = getTaskByCustomerID_StaffID(khach_hang_id, staff_id)
    customer = Khach_hang.query.filter(Khach_hang.id == khach_hang_id).first()
    return render_template("task/detail-task.html", details=details, customer=customer)


@routes.route('/task/create-task', methods=['GET'])
@login_required
def create_task():
    allTask = getALlTask()
    allStaff = getStaff()
    return render_template("task/create.html", existing_tasks=allTask, staffs=allStaff)


@routes.route('/task/update-task/<string:customer_id>/<string:staff_id>/<string:task_id>/<string:id>', methods=['GET'])
@login_required
def update_task(customer_id, staff_id, task_id, id):
    allTask = getALlTask()
    data = getTaskByCustomerID_StaffID(customer_id, staff_id).subquery()
    allTaskCustomer = db.session.query(data).filter(data.c.task_id == task_id, data.c.id == id)
    task_list = []                                 #Vì deadline trong details phải ép thành kiểu datetime-local nên phải tạo biến deadline mới
    for task in allTaskCustomer:
        formatted_task = {}
        formatted_task['id']                = id
        formatted_task['task_id']           = task.task_id
        formatted_task['customer_id']       = task.customer_id
        formatted_task['staff_id']          = task.staff_id
        formatted_task['description']       = task.description
        formatted_task['priority']          = task.priority
        formatted_task['finished']          = task.finished
        formatted_task['note']              = task.note
        formatted_task['extra_description'] = task.extra_description
        print(formatted_task['extra_description'])
        if task.deadline:
            try:
                # Convert to datetime object
                deadline_dt = datetime.strptime(task.deadline, '%d/%m/%Y %H:%M')
                # Format to 'YYYY-MM-DDTHH:MM'
                formatted_task['formatted_deadline'] = deadline_dt.strftime('%Y-%m-%dT%H:%M')
            except ValueError:
                formatted_task['formatted_deadline'] = ''  # In case of formatting error, set to empty string
        else:
            formatted_task['formatted_deadline'] = ''
        task_list.append(formatted_task)
    return render_template('task/edit.html', details=task_list, existing_tasks=allTask)

@routes.route('/spa')
@login_required
def spa():
    payment_list = ['Đủ', 'Nợ']
    price_list = ['Trên 2 triệu', 'Dưới 2 triệu']
    get_treatment_name = (db.session.query(SpaCard, Treatment.name)
                          .join(Card_Treatment, SpaCard.id == Card_Treatment.card_id)
                          .join(Treatment, Card_Treatment.treatment_id == Treatment.id)).subquery()
    card = aliased(get_treatment_name)
    khach_hang = getSpaCardCustomer().all()
    return render_template('spa/main.html',
                           khach_hang=khach_hang,
                           payment_list=payment_list,
                           price_list = price_list
                           )

@routes.route('/spa/create-card', methods=['GET'])
@login_required
def create_card():
    allTreatment = getAllTreatments()
    allStaff     = User_account.query.all()
    return render_template('spa/card-create.html', treatments=allTreatment, staffs=allStaff)

@routes.route('/spa/booking', methods=['GET'])
@login_required
def booking():
    selected_customers = session.get('list_selected_customers')
    allStaff = getStaff()
    allTreatment = getAllTreatments()
    allMask = Mask.query.all()
    booking_data = getAllBookingData()

    staff_json = [{'id': s.id,
                   'name': s.full_name}
                  for s in allStaff]

    mask_json = [{'id':m.id,
                  'mask_name': m.mask_name}
                 for m in allMask]
    return render_template('spa/booking.html',
                           treatments = allTreatment,
                           staffs     = allStaff,
                           booking    = booking_data,
                           staff_json = staff_json,
                           mask_json  = mask_json)

@routes.route('/get-all-card')
def get_all_card():
    cards = getAllCard()
    card = [{'id'         : card.id,
             'customer_id': card.customer_id,
             'total_price': card.total_price,
             'paid'       : card.paid,
             'debt'       : card.debt,
             'note'       : card.note}
            for card in cards]
    return jsonify({'card': card})

@routes.route('/get-card-by-customer-id')
def get_card_by_customer_id():
    customer_id = request.args.get('customer_id')
    cards = getCardByCustomerID(customer_id)
    card = [{'id'         : card.id,
             'customer_id': card.customer_id,
             'total_price': card.total_price,
             'paid'       : card.paid,
             'debt'       : card.debt,
             'note'       : card.note}
            for card in cards]
    return jsonify({'card': card})

@routes.route('/get-treatment-by-card')
def get_treatment_by_card():
    card_id = request.args.get('card_id')
    treatments = getTreatmentByCardID(card_id)
    treatment = [{'name'      : t.name,
                  'total_time': t.total_time,
                  'time_used' : t.time_used,
                  'treatment_id': t.treatment_id}
                 for t in treatments]
    return jsonify({'treatment': treatment})

@routes.route('/get-treatment-by-id')
def get_treatment_by_id():
    treatment_id = request.args.get('treatment_id')
    t = getTreatmentByID(treatment_id)
    treatment = [{'name': t.name,
                  'duration': t.duration}
                 ]

    return jsonify({'treatment': treatment})

@routes.route('/get-customer-by-card')
def get_customer_by_card():
    card_id = request.args.get('card_id')
    c = getCustomerByCard(card_id)
    customer = [{'customer_name': c.ten_khach_hang}]
    return jsonify({'customer': customer})

@routes.route('/spa/report', methods=['GET', 'POST'])
def spa_report():
    if request.method == 'POST':
        return redirect(url_for('routes.spa_report'))
    return render_template('spa/report.html')

@routes.route('/spa/detail/<string:card_id>')
@login_required
def spa_detail(card_id):
    card, customer = (db.session.query(SpaCard, Khach_hang)
                      .filter(SpaCard.id == card_id)
                      .join(Khach_hang, SpaCard.customer_id == Khach_hang.id)
                      .first())
    treatments = getTreatmentByCardID(card_id) # Lấy thông tin liệu trình

    #Lấy tất cả thẻ của người dùng thẻ này
    all_bookings = []
    customer_id = db.session.query(SpaCard.customer_id).filter(SpaCard.id==card_id).first()
    cardOfCurrentCustomer = db.session.query(SpaCard).filter(SpaCard.customer_id == customer_id.customer_id).all()
    for c in cardOfCurrentCustomer:
        booking = getBookingByCardID(c.id)
        all_bookings.extend(booking)

    update_modal = [{'card_id': card.id,
                     'customer_name': customer.ten_khach_hang,
                     'total_price': card.total_price,
                     'paid': card.paid,
                     'debt': card.debt}]
    return render_template('spa/detail.html',
                           customer     = customer,
                           card         = card,
                           treatments   = treatments,
                           booking      = all_bookings,
                           update_modal = update_modal)

@routes.context_processor
def customer_report_url():
    customer_report = url_for('routes.customer_report')
    return dict(customer_report_url=customer_report)
@routes.route('/report/customer_report', methods=['GET'])
def customer_report():
    customer_report = getCustomerCardDetail()
    return render_template('report/customer_report.html', customer_report = customer_report)

@routes.route('/report/mask_report', methods=['GET'])
def mask_report():
    today = datetime.today()
    today = today + timedelta(days=1)
    start_date_default = today - timedelta(days=30)  # 30 ngày trước
    end_date_default = today
    start_date_default_str = start_date_default.strftime('%Y-%m-%d')
    end_date_default_str = end_date_default.strftime('%Y-%m-%d')

    mask_reports = countMaskFromBooking(start_date_default_str, end_date_default_str)
    return render_template('report/mask_report.html',
                           mask_reports = mask_reports,
                           start_date   = start_date_default_str,
                           end_date     = end_date_default_str)

@routes.route('/report/staff_revenue_report', methods=['GET'])
def staff_revenue_report():
    today = datetime.today()
    today = today + timedelta(days=1)
    start_date_default = today - timedelta(days=30)  # 30 ngày trước
    end_date_default = today
    start_date_default_str = start_date_default.strftime('%Y-%m-%d')
    end_date_default_str = end_date_default.strftime('%Y-%m-%d')

    staff_revenue_reports = getRevenueByStaff(start_date_default_str, end_date_default_str)
    for r in staff_revenue_reports:
        print(r)

    # kh = db.session.query(Khach_hang.is_experience, SpaCard.paid).join(SpaCard, Khach_hang.id == SpaCard.customer_id).filter(Khach_hang.is_experience == None).all()
    # print(kh)
    return render_template('report/staff_revenue_report.html',
                           staff_revenue_reports = staff_revenue_reports,
                           start_date            = start_date_default_str,
                           end_date              = end_date_default_str
                           )