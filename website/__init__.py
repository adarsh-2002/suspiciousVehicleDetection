from flask import Flask
from os import path

def create_app():
    print("create_app")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'password'
    app.config['UPLOAD_FOLDER'] = 'static/queryImage'


    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app