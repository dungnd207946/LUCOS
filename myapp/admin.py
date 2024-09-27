from myapp import app
from myapp.templates.config import db
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from myapp.models import Khach_hang, San_pham

admin = Admin(app=app, name='Administrator', template_mode='bootstrap4')

class KhachHangView(ModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    column_searchable_list = ['ten_khach_hang','so_dien_thoai','khu_vuc','nhom_khach_hang' ]
    column_filters = ['ten_khach_hang','so_dien_thoai']
    column_labels = {'ten_khach_hang':'Tên khách hàng',
                     'so_dien_thoai':'Số điện thoại',
                     'khu_vuc':'Khu vực',
                     'dia_chi':'Địa chỉ',
                     'nhom_khach_hang':'Nhóm khách hàng',
                     'ngay_sinh':'Ngày sinh'}

    column_exclude_list = ['email','dia_chi','ngay_sinh']
admin.add_view(KhachHangView(Khach_hang, db.session))

admin.add_view(ModelView(San_pham,db.session))