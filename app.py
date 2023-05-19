from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def result():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome('C:\\Users\\Eren Jaeger\\Downloads\\chromedriver\\chromedriver.exe', chrome_options=options)
    
    id = request.form['id']
    pwd = request.form['password']
        
    driver.get('https://mgc.ibossems.com/')
    driver.maximize_window()

    usr = driver.find_element(By.NAME, "username")
    usr.send_keys(id)

    pas = driver.find_element(By.NAME, "password")
    pas.send_keys(pwd)
    pas.send_keys(Keys.ENTER)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/a[2]/em[1]/span[1]/span[1]")))
    driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/a[2]/em[1]/span[1]/span[1]").click()

    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "ext-gen15")))
    driver.find_element(By.ID, 'ext-gen15').click()

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'x-grid3-cell-inner.x-grid3-col-6')))
    tot_find = driver.find_elements(By.CLASS_NAME, 'x-grid3-cell-inner.x-grid3-col-6')
    tot = [int(i.text.strip(' hours'))for i in tot_find if i.text]

    ab_find = driver.find_elements(By.CLASS_NAME, 'x-grid3-cell-inner.x-grid3-col-7')
    ab = [int(i.text.strip(' hours')) for i in ab_find if i.text]

    pres_find = driver.find_elements(By.CLASS_NAME, 'x-grid3-cell-inner.x-grid3-col-8')
    pres = [int(i.text.strip(' hours')) for i in pres_find if i.text]

    att = sum(pres)/sum(tot)*100
    final = round(att, 2)
    return render_template('result.html', attend = final)

if __name__=='__main__':
    app.run(debug=True)