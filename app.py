from flask import Flask, render_template, url_for, redirect, request, flash, send_from_directory, session, jsonify
import requests
from requests import adapters
import ssl
from urllib3 import poolmanager
import json
import re
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = 'nathaanpuluthi'

@app.route('/')
def home():
    if 'username' in session and 'password' in session:
        # For remembered credentials, render the home page with auto-submit JavaScript
        return render_template('home.html', auto_submit=True, 
                             remembered_username=session['username'], 
                             remembered_password=session['password'])
    return render_template('home.html')

@app.route('/check_another')
def check_another():
    session.clear()
    return redirect(url_for('home'))


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
    
    # Handle both GET (remembered credentials) and POST requests
    if request.method == 'GET':
        if 'username' in session and 'password' in session:
            user = session['username'] 
            pas = session['password']
            remember_me = True
        else:
            # Redirect to home if no stored credentials
            return redirect(url_for('home'))
    else:  # POST request
        user = request.form['username']
        pas = request.form['DOB']
        remember_me = request.form.get('isChecked', False)

    start_time = time.time()
    
    try:
        original_date = datetime.strptime(pas, "%Y-%m-%d")
        formatted_date = original_date.strftime("%y-%m-%d")
    except ValueError:
        return jsonify({'error': 'Please select DOB'})
    
    form_url = 'https://mgc.ibossems.com/'
    result_url = 'https://mgc.ibossems.com/student/'
    list_url = 'https://mgc.ibossems.com/student/attendance/list'
    details_url = 'https://mgc.ibossems.com/student/studentdetails'

    if remember_me:
        session['username'] = user
        session['password'] = pas
    
    try:
        # Step 1: Get initial form
        response1 = req_session.get(form_url, timeout=30)
        if response1.status_code != 200:
            return jsonify({'error': 'Unable to connect to the server. Please try again later.'})
        
        # Step 2: Login
        payload = {
            'username': user,
            'password': formatted_date
        }
        
        response2 = req_session.post(result_url, data=payload, timeout=30)
        if response2.status_code != 200:
            return jsonify({'error': 'Login request failed. Please check your credentials.'})
        
        # Check for login errors
        error = re.findall(r'<p[^>]*>(.*?)</p>', response2.text)
        if error:
            return jsonify({'error': error[0]})
        
        # Step 3: Get student details
        lis_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Mode': 'cors',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        response3 = req_session.get(details_url, headers=lis_headers, timeout=30)
        if response3.status_code != 200:
            return jsonify({'error': 'Unable to fetch student details. Please try again.'})
        
        # Extract student information
        match = re.search(r"name:'student_name',\s+value:'([^']+)'", response3.text)
        department_match = re.search(r"name:'department',\s+value:'([^']+)'", response3.text)
        academic_match = re.search(r"name:'academic',\s+value:'([^']+)'", response3.text)
        
        student_name = match.group(1).strip() if match else "Unknown Student"
        sem = academic_match.group(1) if academic_match else "Unknown Semester"
        dept = department_match.group(1) if department_match else "Unknown Department"
        
        # Step 4: Get attendance data
        lis = {'task': 'LISTING'}
        lis_response = req_session.post(list_url, headers=lis_headers, data=lis, timeout=30)
        
        if lis_response.status_code != 200:
            return jsonify({'error': 'Unable to fetch attendance data. Server returned an error.'})
        
        # Check if response is empty or not JSON
        if not lis_response.text.strip():
            return jsonify({'error': 'No attendance data available. The server returned an empty response.'})
        
        # Try to parse JSON with better error handling
        try:
            data = json.loads(lis_response.text)
        except json.JSONDecodeError as e:
            # Log the actual response for debugging
            print(f"JSON Decode Error: {e}")
            print(f"Response content: {lis_response.text[:500]}...")  # First 500 chars
            print(f"Response status: {lis_response.status_code}")
            print(f"Response headers: {dict(lis_response.headers)}")
            
            # Check if response contains HTML error page
            if '<html' in lis_response.text.lower():
                return jsonify({'error': 'Session expired or invalid. Please try logging in again.'})
            
            return jsonify({'error': 'Invalid response from server. The attendance data could not be processed.'})
        
        # Validate data structure
        if not isinstance(data, dict) or 'attends' not in data:
            return jsonify({'error': 'Invalid attendance data format received from server.'})
        
        if not data['attends']:
            return jsonify({'error': 'No attendance records found for this student.'})
        
        # Process attendance data
        attendance_percentage = []
        cumulative_present = 0
        cumulative_total = 0

        for attend in data['attends']:
            cumulative_present += attend.get('present', 0)
            cumulative_total += attend.get('total', 0)
            percentage = round((cumulative_present / cumulative_total) * 100, 2) if cumulative_total != 0 else 0
            attendance_percentage.append({'date': attend.get('date', 'Unknown'), 'attendance_percentage': percentage})
        
        send = {'od': [], 'absent': [], 'full_abs': []}
        for attend in data['attends']:
            date = attend.get('date', 'Unknown')
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

        present = [i.get('present', 0) for i in data['attends']]
        tot = [i.get('total', 0) for i in data['attends']]
        
        if sum(tot) == 0:
            return jsonify({'error': 'No valid attendance data found.'})
        
        att_percent = round(sum(present) / sum(tot) * 100, 2)
        total_day = len(data['attends'])
        attendance_data = {
            'Present': att_percent,
            'Absent': 100 - att_percent
        }
        
        # Determine year from semester
        try:
            sem_num = int(sem[-1]) if sem and sem[-1].isdigit() else 1
            if sem_num in [1, 2]:
                year = '1st Year'
            elif sem_num in [3, 4]:
                year = '2nd Year'
            else:
                year = '3rd Year'
        except (ValueError, IndexError):
            year = 'Unknown Year'
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Request completed in {elapsed_time:.2f} seconds")
        
        return jsonify({
            'name': student_name,
            'att': att_percent,
            'att_details': send,
            'attendance_percentage': attendance_percentage,
            'semester': sem,
            'year': year,
            'dept': dept,
            'attendance_data': attendance_data,
            'total_days': total_day,
            'tot_abs': tot_absent
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. The server is taking too long to respond. Please try again.'})
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection failed. Please check your internet connection and try again.'})
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return jsonify({'error': 'Network error occurred. Please try again later.'})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route('/health')
def health():
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
