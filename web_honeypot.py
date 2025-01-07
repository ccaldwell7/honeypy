# Libraries
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for

# Logging Format
logging_format = logging.Formatter('%(asctime)s %(message)s')

# HTTP Logger
funnel_logger = logging.getLogger('HTTP Logger') #captures username/password/ipaddress/etc.
funnel_logger.setLevel(logging.INFO) #provides the INFO level of logging
funnel_handler = RotatingFileHandler('http_audits.log', maxBytes=2000, backupCount=5) #rotates the log file after 2000 bytes and keeps 5 backup copies
funnel_handler.setFormatter(logging_format) #sets the format of the log file
funnel_logger.addHandler(funnel_handler) #adds the handler to the logger

# Baseline honeypot

def web_honeypot(input_username="admin", input_password="password"):


    app = Flask(__name__)

    @app.route('/')

    def index():
        return render_template('wp-admin.html')
    
    @app.route('/wp-admin-login', methods=['POST'])

    def login():
        username = request.form['username']
        password = request.form['password']
        
        ip_address = request.remote_addr

        funnel_logger.info(f'Client with IP Address: {ip_address} entered\n Username: {username} and Password: {password}')

        if username == input_username and password == input_password:
            return 'Login successful!'
        else:
            return 'Login failed!'
        
    return app
        

def run_web_honeypot(port=5000, input_username="admin", input_password="password"):
    run_web_honeypot_app = web_honeypot(input_username, input_password)
    run_web_honeypot_app.run(debug=True, port=port, host="0.0.0.0")

    return run_web_honeypot_app


    
