from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import check_password_hash

from .search.routes import search
from .auth.routes import auth
from .models import User

app = Flask(__name__)
login = LoginManager()
moment = Moment(app)
CORS(app)


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

app.register_blueprint(auth)
app.register_blueprint(search)

app.config.from_object(Config)

from .models import db

db.init_app(app)
migrate = Migrate(app, db)
login.init_app(app)


login.login_view = 'auth.logMeIn'


from . import routes
from . import models