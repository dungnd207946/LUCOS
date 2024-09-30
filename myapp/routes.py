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
    create_url = url_for('routes.create_customer')
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
                           amount_product_per_order    = amount_product_per_order)

@routes.route('/khach-hang/them-khach-hang', methods=['GET', 'POST'])
@login_required
def create_customer():
    skin = Skin_type.query.all()
    if request.method == 'POST':
        try:
            id              = request.form['id']
            name            = request.form['name']
            phone_number    = request.form['phone_number']
            khu_vuc         = request.form['khu_vuc']
            address         = request.form['address']
            payment_ability = request.form['payment_ability']
            email           = request.form['email']
            group           = request.form['group']
            birth_date      = request.form['birth_date']
            skin            = request.form['skin']
            new_customer = Khach_hang(id=id,
                                      ten_khach_hang=name,
                                      so_dien_thoai=phone_number,
                                      khu_vuc=khu_vuc,
                                      dia_chi = address,
                                      payment_ability=payment_ability,
                                      skin_property=skin,
                                      email=email,
                                      nhom_khach_hang=group,
                                      ngay_sinh=birth_date,
                                      point=0,
                                      active=1)
            db.session.add(new_customer)
            db.session.commit()
            new_customer_skin = Customer_skin(skin_type_id=skin,
                                              customer_id=new_customer.id)
            db.session.add(new_customer_skin)
            db.session.commit()
            flash('Thêm khách hàng thành công!', 'success')
            return redirect(url_for('routes.infor_khach_hang', khach_hang_id=id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Tạo thẻ thất bại! Vui lòng thử lại.', 'error')
            print(e)  # In lỗi ra console để debug
    return render_template('customer/create-customer.html', skin=skin)

@routes.route('/khach-hang/infor-khach-hang/delete/<string:khach_hang_id>', methods=['DELETE'])
@login_required
@prevent_guest
def delete_khachhang_by_id(khach_hang_id):
    sqlQuery = 'DELETE FROM khach_hang WHERE id = %s'
    return delete(sqlQuery,khach_hang_id)

@routes.route('/khach-hang/update/<string:khach_hang_id>', methods=['GET', 'POST'])
@login_required
@prevent_guest
def update_khach_hang_by_id(khach_hang_id):
    customers = Khach_hang.query.filter(Khach_hang.id == khach_hang_id)
    if request.method == 'POST':
        for customer in customers:
            try:
                customer.ten_khach_hang  = request.form['ten_khach_hang']
                customer.so_dien_thoai   = request.form['so_dien_thoai']
                customer.khu_vuc         = request.form['khu_vuc']
                customer.skin_property   = request.form['skin']
                customer.nhom_khach_hang = request.form['nhom_khach_hang']
                customer.email           = request.form['email']
                customer.point           = request.form['point']
                db.session.commit()
                flash('Cập nhật thông tin khách hàng thành công!', 'success')
                return redirect(url_for('routes.detail_khach_hang', khach_hang_id=khach_hang_id))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('Cập nhật thông tin khách hàng thất bại! Vui lòng thử lại sau.', 'error')
                print(e)  # In lỗi ra console để debug
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
@routes.route('/khach-hang/handle_actions', methods=['POST'])
@login_required
@prevent_guest
def handle_actions():
    if request.method == 'POST':
        action = request.form['action']
        selected_customers = request.form.getlist('selected_customers')
        print(action)
        if action == 'delete':
            for customer_id in selected_customers:
                customer = Khach_hang.query.get(customer_id)
                if customer:
                    db.session.delete(customer)
            db.session.commit()
            flash('Xóa khách hàng thành công!', 'success')
        if action == 'createTask':
            session['list_selected_customers'] = selected_customers  # Lưu danh sách vào session để truyền đi
            return redirect(url_for('routes.create_multi_task'))
        if action == 'booking':
            return redirect(url_for('routes.booking'))

    return redirect(url_for('routes.infor_khach_hang'))

@routes.route('/khach-hang/create-multi-task', methods=['GET', 'POST'])
@login_required
@prevent_guest
def create_multi_task():
    allTask = getALlTask()
    allStaff = getStaff()
    if request.method == 'POST':
        selected_customers = session.get('list_selected_customers')       #Lấy danh sách id từ session
        extra_description  = request.form['new_task']
        staff_id           = request.form['staff']
        task_id            = request.form['existing_task']                       # Nội dung hiện lên form là description, nhưng trả về giá trị là id

        time_str           = request.form['deadline']
        time_obj           = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')  # Chuyển đổi chuỗi thành đối tượng datetime
        deadline           = time_obj.strftime('%d/%m/%Y %H:%M')                    # Chuyển đổi định dạng của thời gian
        priority           = request.form['priority']
        note               = request.form['note']
        for customer_id in selected_customers:
            try:
                new_task_for_customer = Task_Customer(
                    task_id    = task_id,
                    customer_id= customer_id,
                    staff_id   = staff_id,
                    deadline   = deadline,
                    finished   = 0,
                    priority   = priority,
                    note       = note,
                    outdated   = 0,
                    extra_description = extra_description
                )
                db.session.add(new_task_for_customer)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                print(e)  # In lỗi ra console để debug

        flash('Thêm task cho các khách hàng thành công!', 'success')
        return redirect(url_for('routes.infor_khach_hang'))
    return render_template("task/create_for_multi_customer.html", existing_tasks=allTask, staffs=allStaff)

@routes.route('/task', methods=['POST', 'GET'])
@login_required
# @dev_required
def task():
    update_day_without_buying()             # update số ngày chưa mua hàng mỗi khi gọi hàm
    check_task_outdated()
    if current_user.user_role == 'ADMIN':
        table = get_table_task_for_admin()
    else:
        table = get_table_task_for_only_staff()

    staffs = getStaff()
    staffs_ordered = staffs.order_by(User_account.full_name)
    conditions = []
    selected_staff = ''
    if request.method == 'POST':
        table          = table.subquery()
        if current_user.user_role == 'ADMIN':
            selected_staff = request.form['staff']
            if selected_staff != '':
                conditions.append(table.c.staff_id == selected_staff)

        filtered       = db.session.query(table).filter(and_(*conditions)).all()
        return render_template("task/task.html", tables=filtered, staffs=staffs_ordered, selected_staff=selected_staff)
    return render_template("task/task.html", tables=table, staffs=staffs_ordered)

@routes.route('/task/task-detail/<string:khach_hang_id>/<string:staff_id>')
@login_required
def task_detail(khach_hang_id, staff_id):
    details = getTaskByCustomerID_StaffID(khach_hang_id, staff_id)
    customer = Khach_hang.query.filter(Khach_hang.id == khach_hang_id).first()
    return render_template("task/detail-task.html", details=details, customer=customer)


@routes.route('/task/create-task', methods=['GET', 'POST'])
@login_required
@admin_required
def create_task():
    allTask = getALlTask()
    allStaff = getStaff()
    if request.method == 'POST':
        try:
            customer_id       = request.form['customer_id']
            staff_id          = request.form['staff']
            task_id           = request.form['existing_task']  #Nội dung hiện lên form là description, nhưng trả về giá trị là id
            extra_description = request.form['new_task']

            time_str          = request.form['deadline']
            time_obj          = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')  # Chuyển đổi chuỗi thành đối tượng datetime
            deadline          = time_obj.strftime('%d/%m/%Y %H:%M')                    # Chuyển đổi định dạng của thời gian

            priority          = request.form['priority']
            note              = request.form['note']
            new_task_for_customer = Task_Customer(
                task_id           = task_id,
                customer_id       = customer_id,
                staff_id          = staff_id,
                deadline          = deadline,
                finished          = 0,
                priority          = priority,
                note              = note,
                outdated          = 0,
                extra_description = extra_description
            )
            db.session.add(new_task_for_customer)
            db.session.commit()
            print(deadline)
            print('add task success')
            flash('Thêm task thành công!', 'success')
            return redirect(url_for('routes.task'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Thêm task thất bại! Vui lòng thử lại.', 'error')
            print(e)  # In lỗi ra console để debug
    return render_template("task/create.html", existing_tasks=allTask, staffs=allStaff)


@routes.route('/task/update-task/<string:customer_id>/<string:staff_id>/<string:task_id>/<string:id>', methods=['GET', 'POST'])
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

    updateTasks = Task_Customer.query.filter(Task_Customer.id == id)
    if request.method == 'POST':
        for updateTask in updateTasks:
            try:
                updateTask.task_id           = request.form['description']
                updateTask.extra_description = request.form['extra_description']
                # Biến đổi thời gian về dạng string
                time_str                     = request.form['deadline']
                time_obj                     = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')
                updateTask.deadline          = time_obj.strftime('%d/%m/%Y %H:%M')
                updateTask.priority          = request.form['priority']
                finished                     = request.form['finished']
                if finished == 'true':
                    updateTask.finished = True
                else:
                    updateTask.finished = False
                updateTask.note              = request.form['note']
                db.session.commit()
                flash('Cập nhật thông tin task thành công!', 'success')
                return redirect(url_for('routes.task_detail', khach_hang_id=customer_id, staff_id=staff_id))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('Cập nhật thông tin task thất bại! Vui lòng thử lại sau.', 'error')
                print(e)  # In lỗi ra console để debug
    return render_template('task/edit.html', details=task_list, existing_tasks=allTask)

@routes.route('/task/delete/<string:customer_id>/<string:staff_id>/<string:id>', methods=['POST'])
@login_required
def delete_task(customer_id, staff_id, id):
    try:
        task_to_delete = Task_Customer.query.get(id)
        if task_to_delete:
            db.session.delete(task_to_delete)
            db.session.commit()
            flash('Task được xóa thành công!', 'success')
        else:
            flash('Task not found.', 'error')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Xóa task thất bại! Vui lòng thử lại sau.', 'error')
        print(e)  # In lỗi ra console để debug
    return redirect(url_for('routes.task_detail', khach_hang_id=customer_id, staff_id=staff_id))

@routes.route('/check-customer', methods=['POST']) # Hàm để check sự tồn tại của mã khách hàng, dùng trong 'task/create.html'
@login_required
def check_customer():
    customer_id = request.json['customer_id']
    customer = Khach_hang.query.get(customer_id)
    if customer:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

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

@routes.route('/spa/filter', methods=['POST'])
@login_required
def spa_filter():
    if request.method == "POST":
        customers = getSpaCardCustomer()
        payment_list = ['Đủ', 'Nợ']
        price_list = ['Trên 2 triệu', 'Dưới 2 triệu']
        conditions = []

        payment = request.form['payment']
        selected_payment = payment
        if payment == 'Nợ':
            conditions.append(SpaCard.debt > 0)
        if payment == 'Đủ':
            conditions.append(SpaCard.debt == 0)

        price = request.form['price']
        selected_price = price
        if price == 'Trên 2 triệu':
            conditions.append(SpaCard.total_price >= 2000000)
        if price == 'Dưới 2 triệu':
            conditions.append(SpaCard.total_price < 2000000)

        filtered_customers = customers.filter(and_(*conditions))
        return render_template('spa/main.html',
                               khach_hang       = filtered_customers,
                               selected_payment = selected_payment,
                               selected_price   = selected_price,
                               payment_list     = payment_list,
                               price_list       = price_list)

@routes.route('/spa/search', methods=['POST'])
@login_required
@dev_required
def spa_search():
    if request.method == "POST":
        pass
        return render_template('spa/main.html')
@routes.route('/spa/create-card', methods=['GET','POST'])
@login_required
def create_card():
    allTreatment = Treatment.query.all()
    allStaff     = getStaff()
    if request.method == 'POST':
        try:
            customer_id  = request.form['customer_id']
            card_id      = request.form['card_id']
            total_price  = request.form['total_price']
            paid         = request.form['paid']
            debt         = request.form['debt']
            staff        = request.form['staff']
            note         = request.form['note']
            if card_id == '':
                new_card = SpaCard(
                                   customer_id=customer_id,
                                   total_price=total_price,
                                   paid=paid,
                                   debt=debt,
                                   note=note)
            else:
                new_card     = SpaCard(id          = card_id,
                                       customer_id = customer_id,
                                       total_price = total_price,
                                       paid        = paid,
                                       debt        = debt,
                                       note        = note)
            db.session.add(new_card)
            db.session.commit()
            new_card_staff = Card_Staff(card_id  = new_card.id,
                                        staff_id = staff)
            db.session.add((new_card_staff))
            db.session.commit()
            #Lấy số lượng treatment
            treatment_count = len([key for key in request.form.keys() if key.startswith('treatment_id_')])
            for i in range(1, treatment_count + 1):
                treatment_id = request.form[f'treatment_id_{i}']
                price        = request.form[f'price_{i}']
                total_time   = request.form[f'total_time_{i}']
                time_used    = request.form[f'time_used_{i}']

                new_card_treatment = Card_Treatment(card_id      = new_card.id,
                                                    treatment_id = treatment_id,
                                                    price        = price,
                                                    total_time   = total_time,
                                                    time_used    = time_used)
                db.session.add(new_card_treatment)
                db.session.commit()
            flash('Tạo thẻ mới thành công!', 'success')
            return redirect(url_for('routes.spa'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Tạo thẻ thất bại vì mã thẻ bị trùng hoặc sai thao tác! Vui lòng thử lại.', 'error')
            print(e)  # In lỗi ra console để debug
    return render_template('spa/card-create.html', treatments=allTreatment, staffs=allStaff)

@routes.route('/spa/booking', methods=['GET','POST'])
@login_required
def booking():
    selected_customers = session.get('list_selected_customers')
    allStaff = getStaff()
    allTreatment = Treatment.query.all()
    allMask = Mask.query.all()
    result = (db.session.query(SpaBooking, User_account, SpaCard, Khach_hang, Treatment, Mask)
               .join(User_account, SpaBooking.staff_id == User_account.id)
               .join(SpaCard, SpaBooking.card_id == SpaCard.id)
               .join(Khach_hang, SpaCard.customer_id == Khach_hang.id)
               .join(Treatment, SpaBooking.treatment_id == Treatment.id)
               .join(Mask, SpaBooking.mask_id == Mask.id)
               .all())
    print(result)

    booking_data = [
                    {'id'             : booking.id,
                     'staff_id'       : staff.id,
                     'staff_name'     : staff.full_name,
                     'treatment_name' : treatment.name,
                     'duration'       : treatment.duration,
                     'customer_name'  : customer.ten_khach_hang,
                     'date'           : booking.date,
                     'mask_id'        : mask.id,
                     'mask'           : mask.mask_name,
                     'note'           : booking.note,
                     'customer_demand': booking.customer_demand,
                     'status'         : booking.status,
                     'is_new_customer': booking.is_new_customer}
                    for booking, staff, card, customer, treatment, mask in result]

    staff_json = [{'id': s.id,
                   'name': s.full_name}
                  for s in allStaff]

    mask_json = [{'id':m.id,
                  'mask_name': m.mask_name}
                 for m in allMask]
    if request.method == 'POST':
        try:
            customer_id     = request.form.get('customer_id')
            treatment_id    = request.form.get('treatment_id')
            card_id         = request.form.get('card_id')
            mask_id         = request.form.get('mask')
            staff_id        = request.form['staff']
            date            = request.form['date']
            print(date)
            customer_demand = request.form['customer_demand']
            note            = request.form['notes']
            is_new_customer = request.form.get('is_new_customer')
            if is_new_customer:
                staff_money     = 40000
                is_new_customer = 1
            else:
                t               = Treatment.query.filter(Treatment.id == treatment_id).first()
                staff_money     = t.tour_price
                is_new_customer = 0
            new_booking     = SpaBooking(card_id      = card_id,
                                      treatment_id    = treatment_id,
                                      staff_id        = staff_id,
                                      date            = date,
                                      mask_id         = mask_id,
                                      customer_demand = customer_demand,
                                      note            = note,
                                      status          = 1,
                                      staff_money     = staff_money,
                                      is_new_customer = is_new_customer
                                      )
            db.session.add(new_booking)
            db.session.commit()
            flash('Đặt lịch thành công!', 'success')
            return redirect(url_for('routes.booking'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Đặt lịch thất bại! Vui lòng thử lại.', 'error')
            print(e)  # In lỗi ra console  debug
    print("Loggg")
    return render_template('spa/booking.html',
                           treatments = allTreatment,
                           staffs     = allStaff,
                           booking    = booking_data,
                           staff_json = staff_json,
                           mask_json  = mask_json)

@routes.route('/spa/update-booking/<string:id>', methods=['POST'])
def update_booking(id):
    if request.method == 'POST':
        updateBookings = SpaBooking.query.filter(SpaBooking.id == id)
        for updateBooking in updateBookings: # Dù dùng vòng for nhưng updateBooking chỉ là tuple có 1 giá trị
            try:
                updateBooking.staff_id        = request.form.get('staff_modal')
                updateBooking.date            = request.form.get('date_modal')
                updateBooking.mask_id         = request.form.get('mask_modal')
                updateBooking.customer_demand = request.form.get('customer_demand_modal')
                updateBooking.note            = request.form.get('note_modal')
                updateBooking.status          = request.form.get('status_modal_' + str(id))
                if request.form.get('status_modal_' + str(id)) == str(2):
                    # Update_card_treatment ( số lần sử dụng thẻ )
                    update_card_treatment = Card_Treatment.query.filter(Card_Treatment.card_id == updateBooking.card_id,
                                                                        Card_Treatment.treatment_id == updateBooking.treatment_id)
                    for u in update_card_treatment:
                        u.time_used += 1
                        db.session.commit()
                db.session.commit()
                flash('Cập nhật thông tin đặt lịch thành công!', 'success')

            except SQLAlchemyError as e:
                db.session.rollback()
                flash('Cập nhật thông tin đặt lịch thất bại! Vui lòng thử lại sau.', 'error')
                print(e)  # In lỗi ra console để debug
        return redirect(url_for('routes.booking'))

@routes.route('/spa/delete-booking/<string:id>', methods=['POST'])
def delete_booking(id):
    try:
        booking_to_delete = SpaBooking.query.get(id)
        if booking_to_delete:
            db.session.delete(booking_to_delete)
            db.session.commit()
            flash('Lịch đã được xóa thành công!', 'success')
        else:
            flash('Booking not found.', 'error')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Xóa lịch thất bại! Vui lòng thử lại sau.', 'error')
        print(e)  # In lỗi ra console để debug
    return redirect(url_for('routes.booking'))
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
@routes.route('/spa/update-card/<string:id>', methods=['POST'])
@login_required
@admin_required
def update_card(id):
    if request.method == 'POST':
        try:
            updateCards = SpaCard.query.filter(SpaCard.id == id)
            for updateCard in updateCards:
                updateCard.paid = request.form.get('paid_modal')
                updateCard.debt = request.form.get('debt_modal')
                db.session.commit()
                flash('Cập nhật thông tin thanh toán thành công!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Cập nhật thông tin thanh toán thất bại! Vui lòng thử lại sau.', 'error')
            print(e)  # In lỗi ra console để debug
        return redirect(url_for('routes.spa_detail', card_id=id))