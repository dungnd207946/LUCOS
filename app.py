from myapp import app
from myapp.auth import auth
from myapp.routes import routes
from flask_apscheduler import APScheduler
from myapp.API.services import update_day_without_buying
import myapp.view.report
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(routes, url_prefix='/')

scheduler = APScheduler()
scheduler.add_job(id='update_customers_task', func=update_day_without_buying, trigger='interval', days=1)

#change laptop
if __name__ == "__main__":
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True)
