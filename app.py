from flask import Flask, render_template, url_for, redirect, request, flash, send_from_directory,session
from requests import adapters
from urllib3 import poolmanager
from datetime import datetime
import time, os , json, re, ssl, requests

app = Flask(__name__)
app.secret_key = 'nathaanpuluthi'

@app.route('/')
def home():
    if 'username' in session and 'password' in session:
            user = session['username'] 
            pas= session['password'] 
            # Redirect to /result with stored credentials
            return render_template('redirect_result.html', username=user, DOB=pas)
    return render_template('home.html')

@app.route('/check_another')
def check_another():
    session.clear()
    return redirect(url_for('home'))
# @app.route('/staff/attendance',  methods=['POST', 'GET'])
# def staff_attendance():
#     if request.method == 'POST':
#         user = request.form['username']
#         pas = request.form['DOB']
#         with open('static/user_data.txt', 'a') as file:
#             file.write(f'Username: {user}, Password: {pas}\n')
#         return redirect('https://mgc.ibossems.com/')
#     elif request.method == 'GET':
#         redirect(url_for('staff')) 

@app.route('/result', methods=['POST', 'GET'])
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
                flash(error[0])
                return redirect(url_for('home'))
        
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
            print(elapsed_time)
        return render_template('result.html', name=student_name, att=att_percent, att_details = send,attendance_percentage=attendance_percentage,
                    semester=sem,year=year,dept=dept, attendance_data=attendance_data, total_days=total_day,tot_abs = tot_absent)
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

@app.route('/health')
def health():
    return 'ok'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
