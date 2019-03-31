from . import api
from ihome import db
from ihome import models
import logging
from flask import current_app


@api.route('/')
def home():
    return 'this is home page'


@api.route('/index')
def index():
    # logging.erro('错误级别')  # 错误级别
    # logging.warn("警告级别")  # 警告级别
    # logging.info('消息提示级别')  # 消息提示级别
    # logging.debug("调试级别")  # 调试级别
    current_app.logger.error("error message")
    current_app.logger.warn("warn message")
    current_app.logger.info("info message")
    current_app.logger.debug("debug message")
    return "this is index page"
