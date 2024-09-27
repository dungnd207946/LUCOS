from myapp import app
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os


load_dotenv()
mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'dunga3k46pbc2002'
# app.config['MYSQL_DATABASE_DB'] = 'cskh'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.secret_key = 'Dunga3k46pbc2002@'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dunga3k46pbc2002@localhost/cskh?charset=utf8mb4'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.secret_key = 'Dunga3k46pbc2002@'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'

# app.config['MYSQL_DATABASE_USER']     = 'avnadmin'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'AVNS_9tHcBN6z_3iBJ6bWl-b'
# app.config['MYSQL_DATABASE_DB']       = 'lucos'
# app.config['MYSQL_DATABASE_HOST']     = 'mysql-1e356100-dung-4f27.i.aivencloud.com'
# app.secret_key = 'Dunga3k46pbc2002@'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://avnadmin:AVNS_9tHcBN6z_3iBJ6bWl-b@mysql-1e356100-dung-4f27.i.aivencloud.com:10632/lucos?charset=utf8mb4'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mysql.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)