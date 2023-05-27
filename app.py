from flask import Flask, render_template, request, url_for
import requests
from requests import adapters
import ssl
from urllib3 import poolmanager
import json
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def result():
    user = request.form['username']
    pas = request.form['password']
    form_url = 'https://mgc.ibossems.com/'
    result_url = 'https://mgc.ibossems.com/student/'
    list_url = 'https://mgc.ibossems.com/student/attendance/list'
    details_url = 'https://mgc.ibossems.com/student/studentdetails'
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

    session = requests.session()
    session.mount('https://', TLSAdapter())
    response1 = session.get(form_url)
    payload = {
            'username': user,
            'password':pas
        }
    lis = {
        'task':'LISTING'
    }
    lis_headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Sec-Fetch-Mode': 'cors',
    'Content-Type': 'application/x-www-form-urlencoded',
    }
   
    response2 = session.post(result_url, data=payload)
    if response2.status_code == 200:
        response3 = session.get(details_url, headers=lis_headers)
        if response3.status_code == 200:
            match = re.search(r"name:'student_name',\s+value:'([^']+)'", response3.text)
            department_match = re.search(r"name:'department',\s+value:'([^']+)'", response3.text)
            academic_match = re.search(r"name:'academic',\s+value:'([^']+)'", response3.text)
            student_name = match.group(1).strip() if match else None
            sem = academic_match.group(1) if academic_match else None
            dept = department_match.group(1) if department_match else None
                

        lis_response = session.post(list_url, headers=lis_headers, data=lis)
        if lis_response.status_code == 200:
            data = json.loads(lis_response.text)
            present = [i['present'] for i in data['attends']]
            tot = [i['total'] for i in data['attends']]
            att_percent = round(sum(present) / sum(tot) * 100, 2)
    return render_template('result.html', name = student_name, att= att_percent, semester = sem, dept= dept)

if __name__=='__main__':
    app.run(debug=True)