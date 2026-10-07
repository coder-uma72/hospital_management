from flask import Flask
from methods_override import MethodOverrideMiddleware
from config import Config
from models import db, jwt

from routes.auth import auth_bp
from routes.patients import patients_bp
from routes.doctors import doctors_bp
from routes.appointments import appointments_bp
from routes.api import api_bp
from routes.analytics import analytics_bp


app = Flask(__name__)
app.wsgi_app = MethodOverrideMiddleware(app.wsgi_app)

app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(doctors_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(api_bp)
app.register_blueprint(analytics_bp)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Hospital Management System"


if __name__ == "__main__":
    app.run(debug=True)