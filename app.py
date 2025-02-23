from flask import Flask, render_template, url_for, redirect, request, flash, send_from_directory, session, jsonify
from flask_talisman import Talisman
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from urllib.parse import urlparse
from datetime import timedelta
import os
import logging
from requests import adapters
from urllib3 import poolmanager
from datetime import datetime
import time, json, re, ssl, requests



app = Flask(__name__)
app.secret_key = 'nathaanpuluthi'  # Change this to a secure secret key in production

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://ibosstuned.tech", "http://ibosstuned.tech","https://www.ibosstuned.tech", "http://www.ibosstuned.tech" "http://localhost:5000"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "X-Requested-With"]
    }
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Content Security Policy
csp = {
    'default-src': [
        "'self'",
        "https://ibosstuned.tech",
        "https://*.google-analytics.com",
        "https://*.analytics.google.com",
        "https://*.googletagmanager.com",
    ],
    'script-src': [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'",
        "https://cdn.jsdelivr.net",
        "https://code.jquery.com",
        "https://www.googletagmanager.com",
        "https://www.google-analytics.com",
        "https://pagead2.googlesyndication.com",
        "https://fundingchoicesmessages.google.com",
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        "https://cdn.jsdelivr.net",
        "https://fonts.googleapis.com",
        "https://cdnjs.cloudflare.com",
    ],
    'img-src': [
        "'self'",
        "data:",
        "https:",
        "https://www.google-analytics.com",
    ],
    'font-src': [
        "'self'",
        "https://fonts.gstatic.com",
        "https://cdnjs.cloudflare.com",
    ],
    'connect-src': [
        "'self'",
        "https://ibosstuned.tech",
        "https://mgc.ibossems.com",
        "https://www.google-analytics.com",
        "https://*.analytics.google.com",
    ],
    'frame-src': [
        "'self'",
        "https://googleads.g.doubleclick.net",
        "https://fundingchoicesmessages.google.com",
    ],
}

# Configure Talisman based on environment
if app.debug:
    Talisman(app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        force_https=False
    )
else:
    Talisman(app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        force_https=True
    )

# Domain verification decorator
def verify_domain(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        allowed_domains = ['ibosstuned.tech', 'localhost:5000', '127.0.0.1:5000']
        host = request.headers.get('Host', '')
        referer = request.headers.get('Referer', '')
        
        # Allow local development
        if host in ['localhost:5000', '127.0.0.1:5000','192.168.1.21:5000']:
            return f(*args, **kwargs)
            
        # Check if request is from allowed domain
        is_valid = False
        if host in allowed_domains:
            is_valid = True
        if referer:
            referer_domain = urlparse(referer).netloc
            is_valid = is_valid or (referer_domain in allowed_domains)
            
        if not is_valid:
            app.logger.warning(f"Unauthorized access attempt from {host}")
            return jsonify({'error': True, 'message': 'Unauthorized access'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
@verify_domain
def home():
    if 'username' in session and 'password' in session:
        user = session['username'] 
        pas = session['password'] 
        return render_template('redirect_result.html', username=user, DOB=pas)
    return render_template('home.html')

@app.route('/check_another')
@verify_domain
def check_another():
    session.clear()
    return redirect(url_for('home'))

@app.route('/result', methods=['POST', 'GET'])
@verify_domain
@limiter.limit("10 per minute")
def result():
    class TLSAdapter(adapters.HTTPAdapter):

            def init_poolmanager(self, connections, maxsize, block=False):
                ctx = ssl.create_default_context()
                ctx.set_ciphers('DEFAULT@SECLEVEL=1')
                self.poolmanager = poolmanager.PoolManager(
                        num_pools=connections,
                        maxsize=maxsize,
                        block=block,
                        ssl_version=ssl.PROTOCOL_TLS,
                        ssl_context=ctx)

    req_session = requests.session()
    req_session.mount('https://', TLSAdapter())
        
    if request.method == 'POST':
        start_time = time.time()
        user = request.form['username']
        pas = request.form['DOB']
        try:
            original_date = datetime.strptime(pas, "%Y-%m-%d")
            formatted_date = original_date.strftime("%y-%m-%d")
        except ValueError:
            flash('Please select DOB')
            return redirect(url_for('home'))
        form_url = 'https://mgc.ibossems.com/'
        result_url = 'https://mgc.ibossems.com/student/'
        list_url = 'https://mgc.ibossems.com/student/attendance/list'
        details_url = 'https://mgc.ibossems.com/student/studentdetails'
        remember_me = request.form.get('isChecked', False)

        if remember_me:
            session['username'] = user
            session['password'] = pas
        
        response1 = req_session.get(form_url)
        payload = {
                'username': user,
                'password':formatted_date
            }
        lis = {
            'task':'LISTING'
        }
        lis_headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Mode': 'cors',
        'Content-Type': 'application/x-www-form-urlencoded',
        }
        response2 = req_session.post(result_url, data=payload)
        error = re.findall(r'<p[^>]*>(.*?)</p>', response2.text)
        
        if error:
                return jsonify({
                    'error': True,
                    'message': error[0]
                }),400
                
        
        if response2.status_code == 200:
            response3 = req_session.get(details_url, headers=lis_headers)
            if response3.status_code == 200:
                match = re.search(r"name:'student_name',\s+value:'([^']+)'", response3.text)
                department_match = re.search(r"name:'department',\s+value:'([^']+)'", response3.text)
                academic_match = re.search(r"name:'academic',\s+value:'([^']+)'", response3.text)
                student_name = match.group(1).strip() if match else None
                sem = academic_match.group(1) if academic_match else None
                dept = department_match.group(1) if department_match else None
                    

            lis_response = req_session.post(list_url, headers=lis_headers, data=lis)
            if lis_response.status_code == 200:
                data = json.loads(lis_response.text)
                attendance_percentage = []

                cumulative_present = 0
                cumulative_total = 0

                for attend in data['attends']:
                    cumulative_present += attend['present']
                    cumulative_total += attend['total']
                    percentage = round((cumulative_present / cumulative_total) * 100,2) if cumulative_total != 0 else 0
                    attendance_percentage.append({'date': attend['date'], 'attendance_percentage': percentage})
                
                send = {'od': [], 'absent': [], 'full_abs': []}
                for attend in data['attends']:
                    date = attend['date']
                    absent_count = sum(1 for value in attend.values() if value == 'A')

                    if 'OD' in attend.values():
                        desired_keys = [key for key, value in attend.items() if value == 'OD']
                        send['od'].append({date: desired_keys})

                    if 0 < absent_count < 5:
                        tmp = [key for key, value in attend.items() if value == 'A']
                        send['absent'].append({date: tmp})

                    if absent_count == 5:
                        send['full_abs'].append(date)

                tot_absent = len([attend for attend in data['attends'] if sum(1 for value in attend.values() if value == 'A') == 5])

                present = [i['present'] for i in data['attends']]
                tot = [i['total'] for i in data['attends']]
                att_percent = round(sum(present) / sum(tot) * 100, 2)
                total_day = len(data['attends'])
                attendance_data = {
                    'Present': att_percent,
                    'Absent': 100 - att_percent
                }
            if int(sem[-1])== 1 or int(sem[-1])== 2:
                year = '1st Year'
            elif int(sem[-1])== 3 or int(sem[-1])== 4:
                year = '2nd Year'
            else:
                year = '3rd Year'
            end_time = time.time()
            elapsed_time = end_time - start_time
        # return render_template('result.html', name=student_name, att=att_percent, att_details = send,attendance_percentage=attendance_percentage,
        #             semester=sem,year=year,dept=dept, attendance_data=attendance_data, total_days=total_day,tot_abs = tot_absent)
        return jsonify({
        'name': student_name,
        'att': att_percent,
        'semester': sem,
        'year': year,
        'dept': dept,
        'attendance_data': attendance_data,
        'total_days': total_day,
        'tot_abs': tot_absent,
        'att_details': send,
        'attendance_percentage': attendance_percentage
        })
    elif request.method == 'GET':
        if 'username' in session and 'password' in session:
            user = session['username'] 
            pas= session['password'] 
            # Redirect to /result with stored credentials
            return render_template('redirect_result.html', username=user, DOB=pas)
        else:
            # Redirect to home if no stored credentials
            return redirect(url_for('home'))


@app.route('/ads.txt')
def serve_ads_txt():
    return send_from_directory(app.static_folder, 'ads.txt')

@app.route('/privacy')
@verify_domain
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
@verify_domain
def terms():
    return render_template('terms.html')

@app.route('/health')
def health():
    return 'ok'

# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    path = request.path
    app.logger.error(f'Page not found: {path}')
    return render_template("404.html", path=path), 404

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({
        'error': True,
        'message': 'Access denied. This service is only available through ibosstuned.tech'
    }), 403

@app.errorhandler(429)
def ratelimit_error(error):
    return jsonify({
        'error': True,
        'message': 'Too many requests. Please try again later.'
    }), 429

# Security headers middleware
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Request logging middleware
@app.before_request
def log_request():
    app.logger.info(f"Request from {request.remote_addr}: {request.method} {request.url}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if app.debug:
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(host='0.0.0.0', port=port, ssl_context='adhoc')