from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

#DB_NAME = "C:/Users/Deceptacon/Desktop/flaskweb/flaskweb/instance/database.sqlite"
DB_NAME="C:/Users/SHIRAH/Desktop/flaskweb/instance/database.sqlite"
#UPLOAD_FOLDER = 'C:/Users/Deceptacon/Desktop/flaskweb/flaskweb/resumes' 
UPLOAD_FOLDER="C:/Users/SHIRAH/Desktop/flaskweb/resumes"
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    
   
    app.config['SECRET_KEY'] = 'shidah'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['STATIC_FOLDER'] = 'static'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    
    db.init_app(app)

  
    from .auth import auth

    
    app.register_blueprint(auth, url_prefix='/')

    from .models import Job,  Company ,User, Resume

    admin =Admin(app)
    admin.add_view(ModelView(User ,db.session))
    admin.add_view(ModelView(Company ,db.session))
    admin.add_view(ModelView(Resume ,db.session))
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_user'
   
    
    @login_manager.user_loader
    def load_user(user_id):
     company= Company.query.get(int(user_id))
     if company:
        return company
     user = User.query.get(int(user_id))
     if user:
        return user
     job = Job.query.get(int(user_id))
     if job:
        return job
     resume = Resume.query.get(int(user_id))
     if resume:
        return resume

     
    
   
       
    return app