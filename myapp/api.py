import os
from datetime                      import datetime
from flask                         import Blueprint, url_for, request, render_template, flash, redirect, jsonify, session
from flask_login                   import login_required, current_user
from sqlalchemy                    import and_
from sqlalchemy.exc                import SQLAlchemyError
from myapp                         import app
from myapp.Services.report         import countMaskFromBooking, getRevenueByStaff
from myapp.models                  import Khach_hang, Task_Customer, User_account, SpaCard, Treatment, SpaBooking, Card_Treatment, Mask, Card_Staff, Skin_type, Customer_skin
from myapp.API.services            import load_customer
from myapp.Services.task           import get_table_task_for_admin, get_table_task_for_only_staff
from myapp.Services.customer       import getAllCustomers, getGroupCustomerList, getAreaCustomerList
from myapp.Services.user           import getStaff
from myapp.Services.spa            import getSpaCardCustomer, getCustomerCardDetail
from myapp.templates.config        import db
from myapp.auth                    import admin_required, dev_required, prevent_guest
from werkzeug.utils                import secure_filename

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
@api.route('/khach-hang/them-khach-hang', methods=['POST'])
@login_required
@prevent_guest
def create_customer():
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
            gender          = request.form['gender']
            file            = request.files['profile_image']

            if file:
                filename = secure_filename(file.filename)  # Đảm bảo tên file an toàn
                # Kiểm tra và tạo thư mục nếu chưa tồn tại
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                save_path = save_path.replace("\\", "/")
                abs_save_path = 'myapp' + save_path
                file.save(abs_save_path)
                if os.path.exists(abs_save_path):
                    print("File đã được lưu thành công!")
                else:
                    print("Lỗi: Không thể lưu tệp.")
            else:
                save_path = None
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
                                      active=1,
                                      gender=gender,
                                      profile_image=save_path
                                      )
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

@api.route('/khach-hang/update/<string:khach_hang_id>', methods=['POST'])
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

@api.route('/khach-hang/handle_actions', methods=['POST'])
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

@api.route('/khach-hang/create-multi-task', methods=['POST'])
@login_required
@prevent_guest
def create_multi_task():
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
        return redirect(url_for('routes.task'))

@api.route('/task', methods=['POST'])
@login_required
@prevent_guest
def task():
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

@api.route('/task/create-task', methods=['POST'])
@login_required
@prevent_guest
@admin_required
def create_task():
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

@api.route('/task/update-task/<string:customer_id>/<string:staff_id>/<string:task_id>/<string:id>', methods=['POST'])
@login_required
@prevent_guest
@admin_required
def update_task(customer_id, staff_id, task_id, id):
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

@api.route('/task/delete/<string:customer_id>/<string:staff_id>/<string:id>', methods=['POST'])
@login_required
@prevent_guest
@admin_required
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

@api.route('/check-customer', methods=['POST']) # Hàm để check sự tồn tại của mã khách hàng, dùng trong 'task/create.html'
@login_required
def check_customer():
    customer_id = request.json['customer_id']
    customer = Khach_hang.query.get(customer_id)
    if customer:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

@api.route('/spa/filter', methods=['POST'])
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

@api.route('/spa/search', methods=['POST'])
@login_required
@dev_required
def spa_search():
    if request.method == "POST":
        pass
        return render_template('spa/main.html')

@api.route('/spa/create-card', methods=['POST'])
@login_required
@prevent_guest
def create_card():
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
                                   customer_id = customer_id,
                                   total_price = total_price,
                                   paid        = paid,
                                   debt        = debt,
                                   note        = note)
            else:
                new_card = SpaCard(id          = card_id,
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

@api.route('/spa/booking', methods=['POST'])
@login_required
@prevent_guest
def booking():
    if request.method == 'POST':
        try:
            mask_id            = request.form.get('mask')
            staff_id           = request.form['staff']
            date               = request.form['date']
            customer_demand    = request.form['customer_demand']
            note               = request.form['notes']
            is_new_customer    = request.form.get('is_new_customer')
            is_odd_customer    = request.form.get('is_odd_customer') # Khách trải nghiệm
            is_single_customer = request.form.get('is_single_customer') # Khách buổi lẻ
            if is_odd_customer:  #Nếu là khách trải nghiệm thì tạo khách mới, thẻ mới
                customer_id       = request.form['new_customer_id']
                customer_name     = request.form['new_customer_name']
                customer_phone    = request.form['new_customer_phone']
                customer_birthday = request.form['new_customer_birth']
                treatment_id      = request.form['new_customer_treatment']
                price             = request.form['new_customer_treatment_price']
                new_customer      = Khach_hang(id             = customer_id,
                                               ten_khach_hang = customer_name,
                                               so_dien_thoai  = customer_phone,
                                               ngay_sinh      = customer_birthday,
                                               point          = 0,
                                               active         = 1,
                                               is_experience  = 1)
                db.session.add(new_customer)
                db.session.commit()

                #Tạo thẻ mới
                new_card          = SpaCard(customer_id = customer_id, total_price = price, paid = price, debt = 0)
                db.session.add(new_card)
                db.session.commit()

                #Tạo Card_Treatment mới
                card_id            = new_card.id
                new_card_treatment = Card_Treatment(card_id = card_id, treatment_id = treatment_id, price = price,total_time = 1, time_used = 0)
                db.session.add(new_card_treatment)
                db.session.commit()
            elif is_single_customer:
                customer_id = request.form['single_customer_id']
                treatment_id = request.form['single_customer_treatment']
                price = request.form['single_customer_treatment_price']

                # Tạo thẻ mới
                new_card = SpaCard(customer_id=customer_id, total_price=price, paid=price, debt=0)
                db.session.add(new_card)
                db.session.commit()

                # Tạo Card_Treatment mới
                card_id = new_card.id
                new_card_treatment = Card_Treatment(card_id=card_id, treatment_id=treatment_id, price=price, total_time=1, time_used=0)
                db.session.add(new_card_treatment)
                db.session.commit()

            else:
                customer_id  = request.form.get('customer_id')
                treatment_id = request.form.get('treatment_id')
                card_id = request.form.get('card_id')

            # Đổi tiền tour và biến is_new nếu là khách mới, khách trải nghiệm
            if is_new_customer or is_odd_customer:
                staff_money     = 40000
                is_new_customer = 1
            else:
                t               = Treatment.query.filter(Treatment.id == treatment_id).first()
                staff_money     = t.tour_price
                is_new_customer = 0
            # Đổi biến is_single nếu là khách buổi lẻ
            if is_single_customer:
                is_single_book = 1
            else:
                is_single_book = 0
            new_booking     = SpaBooking(card_id      = card_id,
                                      treatment_id    = treatment_id,
                                      staff_id        = staff_id,
                                      date            = date,
                                      mask_id         = mask_id,
                                      customer_demand = customer_demand,
                                      note            = note,
                                      status          = 1,
                                      staff_money     = staff_money,
                                      is_new_customer = is_new_customer,
                                      is_single_book  = is_single_book
                                      )
            db.session.add(new_booking)
            db.session.commit()
            flash('Đặt lịch thành công!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Đặt lịch thất bại! Vui lòng thử lại.', 'error')
            print(e)  # In lỗi ra console  debug
        return redirect(url_for('routes.booking'))

@api.route('/spa/update-booking/<string:id>', methods=['POST'])
@login_required
@prevent_guest
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

@api.route('/spa/delete-booking/<string:id>', methods=['POST'])
@login_required
@prevent_guest
@admin_required
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

@api.route('/spa/update-card/<string:id>', methods=['POST'])
@login_required
@prevent_guest
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

@api.route('/report/customer_report', methods=['POST'])
@login_required
def customer_report():
    if request.method == 'POST':
        number_left = request.form.get('number_left')
        report_data = getCustomerCardDetail(number_left)
        return render_template('report/customer_report.html', customer_report = report_data)

@api.route('/report/mask_report', methods=['POST'])
@login_required
def mask_report():
    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            mask_reports = countMaskFromBooking(start_date_str, end_date_str)
            return render_template('report/mask_report.html',
                                   mask_reports=mask_reports,
                                   start_date=start_date_str,
                                   end_date=end_date_str)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Lọc thất bại! Vui lòng thử lại.', 'error')
            print(e)  # In lỗi ra console  debug
@api.route('/report/staff_revenue_report', methods=['POST'])
@login_required
def staff_revenue_report():
    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            staff_revenue_reports = getRevenueByStaff(start_date_str, end_date_str)
            return render_template('report/staff_revenue_report.html',
                               staff_revenue_reports=staff_revenue_reports,
                               start_date=start_date_str,
                               end_date=end_date_str
                               )
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Lọc thất bại! Vui lòng thử lại.', 'error')
            print(e)  # In lỗi ra console  debug