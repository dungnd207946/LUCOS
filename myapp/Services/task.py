from datetime import datetime

from flask_login import current_user
from myapp.models import Khach_hang, KH_DH, Don_hang, Skin_type, Customer_skin, San_pham, DH_SP, Product_skin, Task_Customer, Task, User_account
from myapp.templates.config import db
from sqlalchemy import func, text, and_, select


def getALlTask():
    result = Task.query.all()
    return result
def getTaskByCustomerID_StaffID(customer_id, staff_id):
    task_by_customer_id       = (db.session.query(Task_Customer, Task.description)
                                 .join(Task, Task_Customer.task_id == Task.id)
                                 .filter(Task_Customer.customer_id == customer_id, Task_Customer.staff_id == staff_id)
                                 .subquery())
    results_order_by_deadline = db.session.query(task_by_customer_id).order_by(task_by_customer_id.c.deadline)
    return results_order_by_deadline

def count_task_by_customer():                          #Chuyển bảng Customer_Task thành bảng customer-staff có bao nhiêu task chưa finish
    result = (db.session.query(
        Task_Customer.customer_id, Task_Customer.staff_id, func.count(Task_Customer.customer_id).label('number_of_task')
    ).filter(Task_Customer.finished == 0)
    .group_by(Task_Customer.customer_id, Task_Customer.staff_id).subquery())

    return result

def customer_with_closest_dealine():                    #Từ Task_Customer lấy ra các khách hàng với deadline gần nhất của họ
    current_date = func.now()
    subquery = (db.session.query(
        Task_Customer.customer_id.label('khach_hang_id'),
        Task_Customer.staff_id,
        func.min(
            func.abs(
                func.timestampdiff(                    #func.abs và func.timestampdiff: Tính toán sự khác biệt giữa ngày hiện tại và deadline.
                    text('SECOND'),                    #Sau đó tìm deadline gần nhất.
                    current_date,
                    func.str_to_date(Task_Customer.deadline, '%d/%m/%Y %H:%i')
                )
            )
        ).label('min_diff'),
        func.min(
            func.str_to_date(Task_Customer.deadline, '%d/%m/%Y %H:%i')
        ).label('closest_deadline')
    )
    .filter(
        and_(
            Task_Customer.finished == 0,
            func.str_to_date(Task_Customer.deadline, '%d/%m/%Y %H:%i') > current_date
        )
    )
    .group_by(Task_Customer.customer_id, Task_Customer.staff_id)
    ).subquery()


    return subquery                                     #Bảng này bao gồm 3 cột: khach_hang_id, staff_id và deadline gần nhất của task ứng với khách hàng
                                                        # Deadline lúc này là kiểu dữ liệu datetime, định dạng sẽ được chuyển đổi ở trong html

def get_table_task():
    number_of_task = count_task_by_customer()           #Lấy số lượng task của 1 khách hàng - nhân viên, bảng này bao gồm khach_hang_id và số lượng task
                                                        #Lấy khach_hang_id, staff_id, số lượng task

    KhachHang_NumberOfTask = db.session.query(number_of_task, Khach_hang.ten_khach_hang).join(
            Khach_hang, Khach_hang.id == number_of_task.c.customer_id
    ).subquery()                                        #Lấy khach_hang_id, staff_id, ten_khach_hang và number_of_task(1)


    closest_deadline = customer_with_closest_dealine()  #Lấy khach_hang_id, staff_id và closest_deadline(2)


    results = (db.session.query(KhachHang_NumberOfTask, closest_deadline)
        .join(closest_deadline, KhachHang_NumberOfTask.c.customer_id == closest_deadline.c.khach_hang_id)
        .filter(KhachHang_NumberOfTask.c.staff_id == closest_deadline.c.staff_id)
               )                                                   #Gộp (1) và (2)

    return results
def change_staff_id_to_name():    #Thêm cột tên staff
    table = get_table_task().subquery()
    result = (db.session.query(table, User_account.full_name.label('staff_name'))
              .join(User_account, table.c.staff_id == User_account.id))

    return result.subquery()

def get_table_task_for_admin():
    Origin_table = change_staff_id_to_name()

    # Sắp xếp kết quả của bảng khách hàng, task theo deadline gần nhất
    return db.session.query(Origin_table).order_by(Origin_table.c.closest_deadline)

def get_table_task_for_only_staff():
    table = get_table_task().subquery()                #Lấy bảng có staff_id để lọc theo từng staff
    query = db.session.query(table).filter(table.c.staff_id == current_user.id).subquery()

    # Sắp xếp kết quả của bảng khách hàng, task theo deadline gần nhất
    return db.session.query(query).order_by(query.c.closest_deadline)

def check_task_outdated():
    task_customers = db.session.query(Task_Customer).all()
    for t in task_customers:
        current_time = datetime.now()
        deadline = datetime.strptime(t.deadline, "%d/%m/%Y %H:%M")
        delta = deadline - current_time
        if delta.total_seconds() < 0:
            t.outdated = True
        else:
            t.outdated = False
    db.session.commit()