from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from dotenv import load_dotenv
import os
#  but when we use after_request , it is not required ! 
# from flask import make_response #----------------------------------------------- prevent browser from caching pages, they must re request ! 

db = SQLAlchemy()
migrate = Migrate()  # <-- NEW


def create_app():
    app = Flask(__name__)

    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    prod = False

    if prod==True:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL_PROD")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")


    # Initialize database and migrate
    db.init_app(app) # used instead of db = SQLAlchemy(app)
    migrate.init_app(app, db)  # <-- NEW

    
    from .routes.auth import auth_bp
    from .routes.summary import summary_bp
    from .routes.main import main_bp
    from .routes.report import report_bp
    from .routes.profile import profile_bp
    from .routes.community import community_bp
    from .routes.leaderboard import leaderboard_bp

     
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(leaderboard_bp)

    

#------------------------------------------------- To prevent browser from caching pages , so after logout , user can see dashboard from cached pages , 
#---------------------------browser must request the page again !!!
    @app.after_request
    def add_cache_control(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


    return app