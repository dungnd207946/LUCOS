from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from myapp.routes import routes
from flask import Blueprint, url_for, request, render_template, flash, redirect, jsonify, session
from flask_login import login_required, current_user
from myapp.Services.report import getStaffReport
from myapp.templates.config import db


@routes.route('/report')
@login_required
def report():
    return render_template('report/main.html')

@routes.context_processor
def common_response_8():
    report_url = url_for('routes.report')
    return {'report_url': report_url}

@routes.route('/report/tour-price', methods=['GET', 'POST'])
@login_required
def tour_price():
    today = datetime.today()
    today = today + timedelta(days=1)
    start_date_default = today - timedelta(days=30)  # 30 ngày trước
    end_date_default = today
    start_date_default_str = start_date_default.strftime('%Y-%m-%d')
    end_date_default_str = end_date_default.strftime('%Y-%m-%d')

    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')  # Ví dụ: '01/09/2024'
            end_date_str = request.form.get('end_date')
            # start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

            staff_report = getStaffReport(start_date_str, end_date_str)
            return render_template('report/tour-price.html',
                                   staff_report=staff_report,
                                   start_date = start_date_str,
                                   end_date = end_date_str)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Lọc thất bại! Vui lòng thử lại.', 'error')
            print(e)  # In lỗi ra console  debug
    else:
        staff_report = getStaffReport(start_date_default_str, end_date_default_str)

    return render_template('report/tour-price.html',
                           staff_report=staff_report,
                           start_date=start_date_default_str,
                           end_date=end_date_default_str)

@routes.context_processor
def common_response_9():
    tour_price_url = url_for('routes.tour_price')
    return {'tour_price_url': tour_price_url}
