from myapp.models import User_account
from myapp.templates.config import db

def getStaff():
    return User_account.query.filter(User_account.user_role == 'USER')
