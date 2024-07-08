# -*- coding: utf-8 -*-
import imaplib, email, json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import sys, os,time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller as AutoChrome
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
from driver_update import chromedriver_update
from option import RunTime

Lms_id = ""
Lms_pw = ""
Lms_url = 'http://edu.semyung.ac.kr/ilos/main/main_form.acl'

Naver_email = ""
Naver_pw = ""

chrome_ver = AutoChrome.get_chrome_version().split('.')[0]
path = os.path.join(os.getcwd(),chrome_ver)
path = os.path.join(path,'chromedriver.exe')
print(path)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--disable-gpu")
options.add_argument("--disable-3d-apis")
chromedriver_update()

def resource_path(relative_path):
    """ dev 및 PyInstaller에 대해 작동하는 리소스에 대한 절대 경로를 가져옵니다. """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path('lmsMacro.ui')
form_class = uic.loadUiType(form)[0]



class Worker(QThread):

    titleBrowser = pyqtSignal(str)  #수강과목 시그널
    chartBrowser = pyqtSignal(str)  #소제목 시그널
    time = pyqtSignal(str)  #시간
    curNum = pyqtSignal(int)
    toNum = pyqtSignal(int)
    result_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.power = False                         # run 매소드 루프 플래그
        self.num = 0
        self.lms_id = ""
        self.lms_pw = ""
        self.naver_email = ""
        self.naver_pw = ""
        self.email_service = EmailServiceNaver(self.naver_email, self.naver_pw)

    def set_email_service(self, email_service):
        self.email_service = email_service
    
    def get_verification_code(self):
        if self.email_service:
            return self.email_service.get_verification_code()
        else:
            return None

    def run(self):
        while self.power:
            driver = webdriver.Chrome(str(path),options= options) #options= options

            driver.get(url=Lms_url)
            driver.implicitly_wait(10)

            login_button = driver.find_element(By.CSS_SELECTOR, "#header > div.utillmenu > ul > a > li")
            login_button.click()    #로그인버튼으로 로그인창으로 넘어가기
            driver.implicitly_wait(10)

            input_id = driver.find_element(By.CSS_SELECTOR, "#usr_id")
            input_pw = driver.find_element(By.CSS_SELECTOR, "#usr_pwd")    

            input_id.send_keys(self.lms_id)      #아이디 입력self.lms_id
            input_pw.send_keys(self.lms_pw)      #비밀번호 입력self.lms_pw

            driver.find_element(By.CSS_SELECTOR, "#login_btn").click()  #최종로그인
             #로그인 실패시
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                # 확인하기
                alert.accept()
                print("로그인 실패")
                self.titleBrowser.emit("LMS 로그인 실패!")
                self.power = False
                self.quit()
            except TimeoutException:
                pass
            driver.implicitly_wait(10)
            #반복문.. 리스트가 없을 때 까지
            while(True):
                if self.power == False:
                    break
                
                
                try:
                    Todo_list_btn = driver.find_element(By.CSS_SELECTOR, "#header > div.utillmenu > div > fieldset > div > div:nth-child(2)")
                    Todo_list_btn.click()   #Todo list 클릭
                    driver.implicitly_wait(10)
                    #온라인강의 클릭
                    driver.find_element(By.CSS_SELECTOR, "#lecture_weeks_cnt").click()
                    driver.implicitly_wait(10)

                    #리스트 중 첫 번째 클릭
                    driver.find_element(By.CLASS_NAME, "todo_wrap.on").click()
                    driver.implicitly_wait(10)

                    # 몇 차시 강의 
                    #chart = driver.find_element(By.ID,"lecture_form")
                    chartlist = driver.find_elements(By.CLASS_NAME,"ibox2")
                    
                    for ibox in range(len(chartlist)):
                        arr=[tr for tr in chartlist]
                        if not self.power:
                            break
                        titleTag = arr[ibox].find_element(By.CSS_SELECTOR, "ul > li:nth-child(1) > ol > li:nth-child(1) > div:nth-child(2)")
                        self.titleBrowser.emit(titleTag.text)
                        print("강의제목 :", titleTag.text,"\n")
                        proidlist = arr[ibox].find_elements(By.CSS_SELECTOR,"#per_text")
                        Time = []
                        Proid = []
                        for i in proidlist:
                            if not self.power:
                                break
                            proid = i.find_element(By.XPATH, '..')
                            timeTag = proid.find_element(By.CSS_SELECTOR, "div:nth-child(3)")
                            Time += [RunTime(timeTag.text)]
                            charts =proid.find_element(By.XPATH, '..')
                            proids =charts.find_element(By.TAG_NAME,"span")
                            Proid += [proids.text]
                        print(Time)
                        #학습 버튼 입력
                        arr[ibox].find_element(By.CSS_SELECTOR,"ul > li:nth-child(2) > img").click()
                        time.sleep(1)
                        self.toNum.emit(len(Time))

                        #다른 기기에서 접속 중
                        try:
                            WebDriverWait(driver, 3).until(EC.alert_is_present())
                            alert = driver.switch_to.alert
                            # 확인하기
                            alert.accept()
                        except TimeoutException:
                            pass
                        time.sleep(1)
                        print("다른기기 접속확인")
                        #if 2차 인증 발생
                        try:
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#secondary_auth_way_wrap > div:nth-child(2)")))
                            driver.find_element(By.CSS_SELECTOR, "#secondary_auth_way_wrap > div:nth-child(2)").click()
                            time.sleep(10)
                            if self.power == False:
                                break
                            # 인증 코드를 최대 3번 시도합니다.
                            for _ in range(3):
                                if self.power == False:
                                    break
                                Auth_Num = self.email_service.get_verification_code()
                                if Auth_Num:
                                    self.result_signal.emit('인증번호 가져오기 성공')
                                else:
                                    self.result_signal.emit('인증번호를 가져올 수 없습니다.')
                                    break

                                WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "secondary_auth_confirm_form")))
                                Auth = driver.find_element(By.CSS_SELECTOR,"#secondary_auth_confirm_input_auth_code_wrap")
                                Auths = Auth.find_elements(By.TAG_NAME, "input")

                                for y, A in enumerate(Auths):
                                    if y==0:
                                        A.click()
                                    A.send_keys(Auth_Num[y])
                                    print(Auth_Num[y])
                                    time.sleep(0.1)

                                driver.implicitly_wait(10)

                                print("=================================")
                                print(driver.find_element(By.CSS_SELECTOR, "#btnConfirmSecondaryAuth").get_attribute('innerHTML'))

                                driver.execute_script('confirmSecondaryAuth();')
                                time.sleep(1)

                                # 경고창이 있는지 확인합니다.
                                alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
                                if alert:
                                    alert.accept()
                                    print("인증 실패. 다시 시도합니다.")
                                    time.sleep(5)
                                    continue
                                else:
                                    break
                            else:
                                self.result_signal.emit('2차 인증 3회 실패')
                                break

                        except Exception as e:
                            print(f"인증 과정에서 예외가 발생했습니다: {e}")
                            pass
                        time.sleep(1)

                        print("인증완료")
                        index = 0
                        print(len(Time))
                        for i in range(len(Time)):
                            if self.power == False:
                                break
                            self.chartBrowser.emit(Proid[i])
                            print(Proid[i])
                            print(Time[i])
                            if Time[i] <= 0:
                                index += 1
                                print("index= ",i)
                                self.time.emit(str(Time[i]))
                                self.curNum.emit(index + 1)
                            elif Time[i] > 0:
                                driver.implicitly_wait(10)
                                try:
                                    driver.switch_to.frame('contentViewer')
                                    driver.implicitly_wait(10)
                                    self.curNum.emit(index+1)
                                    print("index= ",i)
                                    try:
                                        #재생버튼
                                        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID,"test_player"))).send_keys(Keys.SPACE)
                                        #driver.find_element(By.XPATH,'//*[@id="test_player"]/button').send_keys(Keys.SPACE)
                                        driver.implicitly_wait(1)
                                        #음소거버튼
                                        driver.find_element(By.CSS_SELECTOR, "#test_player > div.vjs-control-bar > div.vjs-volume-panel.vjs-control.vjs-volume-panel-horizontal > button").click()
                                        driver.implicitly_wait(1)
                                    except Exception as e:
                                        print(f"재생버튼 요소를 찾지 못하였습니다.: {e}")
                                        pass
                                    driver.switch_to.default_content()
                                except Exception as e:
                                    print(f"contentViewer 프레임을 찾지 못하였습니다.: {e}")
                                    pass
                                
                                num_of_secs = Time[i]
                                while num_of_secs:
                                    if self.power == False:
                                        break
                                    h, num_of_min = divmod(num_of_secs, 3600)
                                    m, s = divmod(num_of_min, 60)
                                    min_sec_format = '{:02d}:{:02d}:{:02d}'.format(h, m, s)
                                    self.time.emit(min_sec_format)
                                    print(min_sec_format, end='\r')
                                    time.sleep(1)
                                    num_of_secs -= 1
                                index += 1
                            
                            if (index) == len(Time):
                                driver.find_element(By.CSS_SELECTOR, "#close_").click()
                                #time.sleep(0.5)
                                #경고창 발생 학습이 완료되지 않았는가?
                                try:
                                    WebDriverWait(driver, 1).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    # 확인하기
                                    alert.dismiss()
                                except TimeoutException:
                                    pass
                                print("종료")
                            else:
                                driver.find_element(By.CSS_SELECTOR, "#next_").click()
                                time.sleep(1)
                                #경고창 발생 학습이 완료되지 않았는가?
                                try:
                                    WebDriverWait(driver, 1).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    # 확인하기
                                    alert.dismiss()
                                except TimeoutException:
                                    pass
                                print("다음")
                        
                        driver.refresh()
                        del arr[:]
                        time.sleep(1)
                        chartlist = driver.find_elements(By.CLASS_NAME,"ibox2")
                            

                except ElementClickInterceptedException:
                    print("온라인 강의가 없습니다.")
                    self.titleBrowser.emit("수강 완료!~")
                    self.power = False
                    self.quit()
                    break
            

    def stop(self):
        # 멀티쓰레드를 종료하는 메소드
        self.power = False
        self.quit()
        self.wait(3000)  # 3초 대기 (바로 안꺼질수도)
        self.titleBrowser.emit("중지...")

class EmailServiceNaver(QThread):
    verification_code_signal = pyqtSignal(str)

    def __init__(self, email_address, password):
        super().__init__()
        self.email_address = email_address
        self.password = password
        self.verification_code = None

    def run(self):
        print(self.email_address, self.password)
        print(self.email_address,"이메일 로그인시작")
        mail = imaplib.IMAP4_SSL("imap.naver.com", 993)
        mail.login(self.email_address, self.password)
        print("이메일 로그인 완료")
        mail.select("inbox")

        # Set the search criteria
        sender = "세명대학교"
        subject_keyword = "[세명대학교] 요청하신 인증번호입니다."
        since_date = (datetime.now() - timedelta(minutes=15)).strftime("%d-%b-%Y")
        search_criteria = f'(SINCE "{since_date}") UNSEEN FROM "{sender}" SUBJECT "{subject_keyword}"'.encode("utf-8")
        num_retries = 3

        for i in range(num_retries):
            try:
                _, message_numbers = mail.search(None, search_criteria)

                # Get the emails
                message_numbers_list = message_numbers[0].split()

                if not message_numbers_list:
                    print("No matching email found. Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    latest_email_number = message_numbers_list[-1]

                    # Get the latest email
                    _, msg_data = mail.fetch(latest_email_number, "(RFC822)")
                    msg = email.message_from_bytes(msg_data[0][1])
                    # Extract the email content
                    content = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                content += part.get_payload(decode=True).decode()
                    else:
                        content = msg.get_payload(decode=True).decode()
                        print(content)

                    mail.store(latest_email_number, '+FLAGS', '\\Seen')
                    mail.logout()
                    soup = BeautifulSoup(content, 'html.parser')
                    verification_code_span = soup.find('span', {'style': 'display:inline-block; margin-left:16px; vertical-align:middle; font-size:21px; font-weight:bold; color:#1aa3ff;'})

                    if verification_code_span:
                        self.verification_code = verification_code_span.text.strip()
                        print("인증번호:", self.verification_code)
                        self.verification_code_signal.emit(self.verification_code)
                        break
                    else:
                        print("인증번호를 찾을 수 없습니다. Retrying in 10 seconds...")
                        time.sleep(10)
            except Exception as e:
                print("에러 발생:", e)
                print("10초 후 재시도합니다...")
                time.sleep(10)
            

    def get_verification_code(self):
        loop = QEventLoop()
        self.verification_code_signal.connect(loop.quit)
        self.start()
        loop.exec_()
        return self.verification_code

class EmailServiceGmail(QThread):
    verification_code_signal = pyqtSignal(str)

    def __init__(self, email_address, password):
        super().__init__()
        self.email_address = email_address
        self.password = password
        self.verification_code = None

    def run(self):
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(self.email_address, self.password)
        mail.select("inbox")

        # Set the search criteria
        sender = "세명대학교"
        subject_keyword = "[세명대학교] 요청하신 인증번호입니다."
        since_date = (datetime.now() - timedelta(minutes=15)).strftime("%d-%b-%Y")
        search_criteria = f'(SINCE "{since_date}") UNSEEN FROM "{sender}" SUBJECT "{subject_keyword}"'.encode("utf-8")

        num_retries = 3

        for i in range(num_retries):
            try:
                _, message_numbers = mail.search(None, search_criteria)

                # Get the emails
                message_numbers_list = message_numbers[0].split()

                if not message_numbers_list:
                    print("No matching email found. Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    latest_email_number = message_numbers_list[-1]

                    # Get the latest email
                    _, msg_data = mail.fetch(latest_email_number, "(RFC822)")
                    msg = email.message_from_bytes(msg_data[0][1])
                    if self.power == False:
                        break
                    # Extract the email content
                    content = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                content += part.get_payload(decode=True).decode()
                    else:
                        content = msg.get_payload(decode=True).decode()
                        print(content)

                    mail.store(latest_email_number, '+FLAGS', '\\Seen')
                    mail.logout()

                    soup = BeautifulSoup(content, 'html.parser')
                    verification_code_span = soup.find('span', {'style': 'display:inline-block; margin-left:16px; vertical-align:middle; font-size:21px; font-weight:bold; color:#1aa3ff;'})

                    if verification_code_span:
                        self.verification_code = verification_code_span.text.strip()
                        print("인증번호:", self.verification_code)
                        self.verification_code_signal.emit(self.verification_code)
                        break
                    else:
                        print("인증번호를 찾을 수 없습니다. Retrying in 10 seconds...")
                        time.sleep(10)
            except Exception as e:
                print("에러 발생:", e)
                print("10초 후 재시도합니다...")
                time.sleep(10)

    def get_verification_code(self):
        loop = QEventLoop()
        self.verification_code_signal.connect(loop.quit)
        self.start()
        loop.exec_()
        return self.verification_code

class EmailServiceDaum(QThread):
    verification_code_signal = pyqtSignal(str)

    def __init__(self, email_address, password):
        super().__init__()
        self.email_address = email_address
        self.password = password
        self.verification_code = None

    def run(self):
        mail = imaplib.IMAP4_SSL("imap.daum.net", 993)
        mail.login(self.email_address, self.password)
        mail.select("inbox")

        # Set the search criteria
        sender = "세명대학교"
        subject_keyword = "[세명대학교] 요청하신 인증번호입니다."
        since_date = (datetime.now() - timedelta(minutes=15)).strftime("%d-%b-%Y")
        search_criteria = f'(SINCE "{since_date}") UNSEEN FROM "{sender}" SUBJECT "{subject_keyword}"'

        num_retries = 3

        for i in range(num_retries):
            try:
                _, message_numbers = mail.search(None, search_criteria.encode('utf7'))

                # Get the emails
                message_numbers_list = message_numbers[0].split()

                if not message_numbers_list:
                    print("No matching email found. Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    latest_email_number = message_numbers_list[-1]

                    # Get the latest email
                    _, msg_data = mail.fetch(latest_email_number, "(RFC822)")
                    msg = email.message_from_bytes(msg_data[0][1])

                    # Extract the email content
                    content = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                content += part.get_payload(decode=True).decode()
                    else:
                        content = msg.get_payload(decode=True).decode()
                        print(content)

                    mail.store(latest_email_number, '+FLAGS', '\\Seen')
                    mail.logout()

                    soup = BeautifulSoup(content, 'html.parser')
                    verification_code_span = soup.find('span', {'style': 'display:inline-block; margin-left:16px; vertical-align:middle; font-size:21px; font-weight:bold; color:#1aa3ff;'})

                    if verification_code_span:
                        self.verification_code = verification_code_span.text.strip()
                        print("인증번호:", self.verification_code)
                        self.verification_code_signal.emit(self.verification_code)
                        break
                    else:
                        print("인증번호를 찾을 수 없습니다. Retrying in 10 seconds...")
                        time.sleep(10)
            except Exception as e:
                print("에러 발생:", e)
                print("10초 후 재시도합니다...")
                time.sleep(10)
        
    def get_verification_code(self):
        loop = QEventLoop()
        self.verification_code_signal.connect(loop.quit)
        self.start()
        loop.exec_()
        return self.verification_code
    
class MainWindow(QMainWindow, form_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        window_ico = resource_path('lmsMacro.ico')
        self.setWindowIcon(QIcon(window_ico)) #아이콘 설정

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.settings_path = os.path.join(dir_path, 'settings.json')
        
        # thread start
        self.worker = Worker()
        self.worker.start()
        self.worker.titleBrowser.connect(self.title)
        self.worker.chartBrowser.connect(self.proid)
        self.worker.time.connect(self.timeout)
        self.worker.curNum.connect(self.curnum)
        self.worker.toNum.connect(self.tonum)
        
        self.saveButton.clicked.connect(self.btn_clicked)
        self.startButton.clicked.connect(self.btnRun_clicked)
        self.stopButton.clicked.connect(self.btnStop_clicked)
        self.radio_naver.setChecked(True)
        # check if settings file exists
        if os.path.exists(self.settings_path):
            self.load_settings()
        else:
            self.lms_id_textEdit.setPlainText('')
            self.lms_pw_lineEdit.setText('')
            self.email_address_textEdit.setPlainText('')
            self.email_password_textEdit.setText('')
            # 저장 버튼을 눌러 초기값을 저장
            self.btn_clicked()

    def btn_clicked(self):
        QMessageBox.about(self, "로그인", "저장되었습니다.")
        self.worker.lms_id = self.lms_id_textEdit.toPlainText()
        self.worker.lms_pw = self.lms_pw_lineEdit.text()

        email_address = self.email_address_textEdit.toPlainText()
        password = self.email_password_textEdit.text()

        if self.radio_naver.isChecked():
            email_service = EmailServiceNaver(email_address, password)
        elif self.radio_gmail.isChecked():
            email_service = EmailServiceGmail(email_address, password)
        elif self.radio_daum.isChecked():
            email_service = EmailServiceDaum(email_address, password)
        else:
            print('이메일이 선택되지 않았습니다.')
            return

        self.save_settings()

        self.worker.email_service = email_service
        self.worker.result_signal.connect(self.on_worker_result)
        self.worker.start()
    
    def btnRun_clicked(self):
        self.worker.power = True
        self.worker.start()

    def btnStop_clicked(self):
        self.worker.power = False
        QMessageBox.about(self, "시스템", "중지완료.")
    
    def on_worker_result(self, result):
        print(result)

    @pyqtSlot(str)
    def title(self, title):
        self.titleBrowser.setText(str(title))

    @pyqtSlot(str)
    def timeout(self, time):
        self.lcdNumber.display(time)

    @pyqtSlot(str)
    def proid(self, proid):
        self.chartBrowser.setText(str(proid))

    @pyqtSlot(int)
    def curnum(self, cnum):
        self.curNumlcd.display(cnum)

    @pyqtSlot(int)
    def tonum(self, tnum):
        self.toNumlcd.display(tnum)

    def save_settings(self):
        settings = {}
        settings['lms_id'] = self.lms_id_textEdit.toPlainText()
        settings['lms_pw'] = self.lms_pw_lineEdit.text()
        settings['email_address'] = self.email_address_textEdit.toPlainText()
        settings['email_password'] = self.email_password_textEdit.text()

        if self.radio_naver.isChecked():
            settings['email_service'] = 'naver'
        elif self.radio_gmail.isChecked():
            settings['email_service'] = 'gmail'
        elif self.radio_daum.isChecked():
            settings['email_service'] = 'daum'
        else:
            settings['email_service'] = None

        with open(self.settings_path, 'w+') as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)

            self.lms_id_textEdit.setPlainText(settings.get('lms_id', ''))
            self.lms_pw_lineEdit.setText(settings.get('lms_pw', ''))
            self.email_address_textEdit.setPlainText(settings.get('email_address', ''))
            self.email_password_textEdit.setText(settings.get('email_password', ''))
            self.worker.lms_id = settings.get('lms_id', '')
            self.worker.lms_pw = settings.get('lms_pw', '')
            email_address = settings.get('email_address', '')
            password = settings.get('email_password', '')
            email_service = settings.get('email_service', None)
            if email_service == 'naver':
                print("naver")
                self.radio_naver.setChecked(True)
                email_service = EmailServiceNaver(email_address, password)
            elif email_service == 'gmail':
                print("gmail")
                self.radio_gmail.setChecked(True)
                email_service = EmailServiceGmail(email_address, password)
            elif email_service == 'daum':
                print("daum")
                self.radio_daum.setChecked(True)
                email_service = EmailServiceDaum(email_address, password)

        except FileNotFoundError:
            pass
        
    def closeEvent(self, event):
        quit_msg = "프로그램을 종료하시겠습니까?"
        self.save_settings()
        reply = QMessageBox.question(self, '메세지', quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 멀티쓰레드를 종료하는 stop 메소드를 실행함
            self.worker.stop()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True) # 아이콘 해상력 높이기
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
