from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from myapp.templates.config import login, db
from myapp.API.services import add_user, check_login
from myapp.models import User_account

from functools import wraps

auth = Blueprint('auth', __name__, static_folder='static', template_folder='templates')

@login.user_loader
def load_user(user_id):
    return User_account.query.get(user_id)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.user_role != 'ADMIN':
            print("Cần quyền admin")
            flash('Chỉ ADMIN mới có quyền truy cập.', 'error')
            return redirect(request.referrer)
        return f(*args, **kwargs)
    return decorated_function
def dev_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_role != 'DEV':
            flash('Chức năng đang được bảo trì!', 'error')
            return redirect(request.referrer)
        return f(*args, **kwargs)
    return decorated_function
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.user_role != 'ADMIN' or current_user.user_role != 'USER':
            print("Cần quyền admin")
            flash('Người dùng thử không có quyền truy cập.', 'error')
            return redirect(request.referrer)
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login_page():
    message = ''
    if request.method == 'POST':
        username      = request.form.get('username')
        user_password = request.form.get('user_password')
        user          = check_login(username, user_password)
        if user:
            login_user(user)
            if current_user.is_authenticated:
                return redirect(url_for('routes.dash_board'))
                # return redirect(url_for('routes.dash_board'))
            else:
                message = 'Đăng nhập thất bại!'
            return redirect(url_for('routes.dash_board'))
        else:
            message   = 'Tài khoản hoặc mật khẩu không đúng!'
    return render_template('auth/login.html', message=message)

@auth.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('auth.login_page'))

@auth.route('/register-box', methods=['GET', 'POST'])
# @dev_required
# @admin_required
def register_page():
    message = ''
    if request.method == 'POST':
        full_name         = request.form.get('fullname')
        username         = request.form.get('username')
        user_password    = request.form.get('user_password')
        confirm_password = request.form.get('confirm_password')
        phone_number     = request.form.get('phone_number')
        user_role        = request.form.get('user_role')
        try:
            if user_password.strip().__eq__(confirm_password.strip()):
                existing_user = User_account.query.filter_by(username=username).first()
                if existing_user:
                    message = 'Username đã tồn tại!'
                else:
                    message = 'Đăng kí thành công! Hãy đăng nhập hệ thống!'
                    add_user(full_name      = full_name,
                             username       = username,
                             user_password  = user_password,
                             phone_number   = phone_number,
                             user_role      = user_role)
                    #return redirect(url_for('auth.register_page', message=message))
            else:
                message = 'Mật khẩu không trùng khớp!'
        except Exception as e:
            message = 'Hệ thống đang có lỗi!!!' #+ str(e)
    return render_template('auth/register.html', message=message)


