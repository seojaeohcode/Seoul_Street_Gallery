from flask import Flask
from datetime import timedelta

application = Flask(__name__)
application.secret_key = 'secretkey'

# load configuration
application.config.from_object('config')
application.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=300) # 로그인 지속시간을 정합니다. 현재 1분

# import routes
from backend import routes