from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_uploads import IMAGES,UploadSet,configure_uploads,patch_request_class
import os
from flask_msearch import Search
basedir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='61ab08586c8528caca2915e2'
app.config["UPLOADED_PHOTOS_DEST"]=os.path.join(basedir,'static/images')
#This indicates the directory uploaded files will be saved to.

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app) 


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

search = Search()
search.init_app(app)
from market import routes
from market.cartss import carts