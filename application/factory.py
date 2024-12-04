import os
import yaml
from pathlib import Path
import importlib.resources as pkg_resources

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()
env = os.getenv('MY_ENV', 'dev')


with pkg_resources.path('dg_spider.resources.config', 'config.yaml') as datafile:
    with open(datafile, 'r', encoding='utf-8') as f:
        my_yaml = yaml.safe_load(f)
        my_cfg = my_yaml['default']
        my_cfg.update(my_yaml[env])


def init_app() -> Flask:
    app: Flask = Flask(__name__)
    app.BASE_DIR = Path(__file__).resolve().parent.parent

    # mysql
    db_config = my_cfg['mysql']
    db_url = 'mysql+pymysql://{username}:{password}@{host}:{port}/{db}?autocommit=true'.format(**db_config)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SQLALCHEMY_ECHO"] = True

    # debug
    # app.config["DEBUG"] = True if env == 'dev' else False
    app.config["DEBUG"] = False

    db.init_app(app)
    return app

