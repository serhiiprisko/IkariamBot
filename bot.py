
import time
import json
import requests
import base64
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from subprocess import CREATE_NO_WINDOW

from settings import Settings

from PyQt6.QtCore import QThread, pyqtSignal


def init_chrome_driver(proxy, test):
    chrome_service = ChromeService('chromedriver')
    chrome_service.creation_flags = CREATE_NO_WINDOW

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if proxy == '':
        chrome_driver = webdriver.Chrome(
            'chromedriver.exe', options=options, service=chrome_service)
    else:
        _proxy = Proxy()
        _proxy.proxy_type = ProxyType.MANUAL
        _proxy.http_proxy = proxy
        _proxy.ssl_proxy = proxy

        capabilities = webdriver.DesiredCapabilities.CHROME
        _proxy.add_to_capabilities(capabilities)
        chrome_driver = webdriver.Chrome(
            'chromedriver.exe', options=options, desired_capabilities=capabilities, service=chrome_service)

    if test == True:
        chrome_driver.get("https://whatismyipaddress.com")
    else:
        # chrome_driver.set_window_position(-10000, 0)
        # chrome_driver.get("https://www.google.com/")
        chrome_driver.get("https://lobby.ikariam.gameforge.com/")
    return chrome_driver


def extract_text():
    with open('__temp.jpg', 'rb') as file:
        encoded_string = base64.b64encode(file.read()).decode('ascii')

    print("sending request...")
    url = 'https://api.apitruecaptcha.org/one/gettext'
    data = {
        'userid': 'Caroz',
        'apikey': 'PI6SyjJvLg0lWBEgthV9',
        'data': encoded_string,
        'case': 'mixed',
        'mode': 'human'
    }
    response = requests.post(url=url, json=data)
    data = response.json()
    print(data)
    return data['result']


class Bot(QThread):
    statusSignal = pyqtSignal(str)
    pointsSignal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.m_isRunning = False
        self.m_isPaused = False
        self.m_test = False
        self.action = ""

    def sleep_random(self):
        delay = Settings.widget_inst.get_delay()
        time.sleep(delay)

    def chrome_available(self):
        try:
            self.chrome_driver.title
            return True
        except:
            return False

    def find_element(self, key, value):
        while True:
            try:
                return self.chrome_driver.find_element(
                    key, value)
            except:
                if self.chrome_available() == False or self.m_isRunning == False:
                    return None
            time.sleep(1)

    def find_element_children(self, parent, key, value):
        while True:
            try:
                return parent.find_element(
                    key, value)
            except:
                if self.chrome_available() == False or self.m_isRunning == False:
                    return None
            time.sleep(1)

    def find_elements(self, key, value, index):
        while True:
            try:
                return self.chrome_driver.find_elements(
                    key, value)[index]
            except:
                if self.chrome_available() == False or self.m_isRunning == False:
                    return None
            time.sleep(1)

    def find_elements_children(self, parent, key, value, index):
        while True:
            try:
                return parent.find_elements(
                    key, value)[index]
            except:
                if self.chrome_available() == False or self.m_isRunning == False:
                    return None
            time.sleep(1)

    def login_game(self):
        self.statusSignal.emit('Waiting for login...')
        print('find accept cookie button')
        acceptCookie = self.find_elements(By.CLASS_NAME, "cookiebanner5", 1)
        if acceptCookie == None:
            return False
        self.chrome_driver.execute_script(
            "arguments[0].click();", acceptCookie)
        print('click login on login/register tab')
        loginRegisterTabs = self.find_element("id", "loginRegisterTabs")
        if loginRegisterTabs == None:
            return False
        loginRegisterTabs.find_elements(By.TAG_NAME, "li")[0].click()
        print('find login form')
        loginForm = self.find_element("id", "loginForm")
        if loginForm == None:
            return False
        print('enter email')
        loginForm_email = self.find_element_children(
            loginForm, "name", "email")
        if loginForm_email == None:
            return False
        loginForm_email.send_keys(self.m_username)
        print('enter password')
        loginForm_password = self.find_element_children(
            loginForm, "name", "password")
        if loginForm_password == None:
            return False
        loginForm_password.send_keys(self.m_password)
        print('submit login form')
        loginForm = self.find_element("id", "loginForm")
        if loginForm == None:
            return False
        loginForm.submit()
        return True

    def enter_arena(self):
        self.statusSignal.emit('Entering arena...')
        print('find join game')
        joinGame = self.find_element("id", "joinGame")
        if joinGame == None:
            return False
        time.sleep(3)
        print('click last played')
        lastPlayed = self.find_elements_children(
            joinGame, By.TAG_NAME, "button", 1)
        if lastPlayed == None:
            return False
        self.chrome_driver.execute_script(
            "arguments[0].click();", lastPlayed)
        print('waiting for 2 tabs')
        while len(self.chrome_driver.window_handles) < 2:
            if self.chrome_available() == False:
                return False
            time.sleep(1)
        print('switching tab')
        self.chrome_driver.switch_to.window(
            self.chrome_driver.window_handles[1])
        while self.chrome_driver.title == "Ikariam - Build, Conquer and Reign!":
            if self.chrome_available() == False:
                return False
            time.sleep(1)
        print('close first tab')
        before_window = self.chrome_driver.window_handles[0]
        after_window = self.chrome_driver.window_handles[1]
        self.chrome_driver.switch_to.window(before_window)
        self.chrome_driver.close()
        self.chrome_driver.switch_to.window(after_window)
        time.sleep(5)
        return True

    def open_fortress_if_not_exist(self):
        if self.check_if_exist("pirateCaptureBox") == True:
            return
        print("opening fortress")
        # self.statusSignal.emit('Opening fortress...')
        pirateFortress = self.find_element(
            "xpath", "//div[contains(@class, 'building pirateFortress')]")
        if pirateFortress == None:
            return False
        pirateFortress = self.find_elements_children(
            pirateFortress, By.TAG_NAME, "a", 0)
        if pirateFortress == None:
            return False
        self.chrome_driver.execute_script(
            "arguments[0].click();", pirateFortress)
        time.sleep(5)
        return True

    def close_popup_if_exist(self):
        try:
            popup = self.chrome_driver.find_element("id", "multiPopup")
            self.chrome_driver.execute_script(
                "arguments[0].parentNode.removeChild(arguments[0]);", popup)
            print('closed popup')
            time.sleep(3)
        except:
            return

    def solve_captcha_if_exist(self):
        try:
            captcha = self.chrome_driver.find_element("id", "captcha")
            pirateCaptureBox = self.find_element("id", "pirateCaptureBox")
            content = pirateCaptureBox.find_element(By.CLASS_NAME, "content")

            print("solving captcha...")
            img = self.find_element_children(content, By.TAG_NAME, "img")

            self.show()
            actions = ActionChains(self.chrome_driver)
            actions.move_to_element(img).perform()

            print(img.get_attribute("src"))
            with open('__temp.jpg', 'wb') as file:
                file.write(img.screenshot_as_png)
            self.hide()

            code = extract_text()
            if code == "":
                return
            captcha.send_keys(code)
            captcha_form = self.find_element_children(
                content, By.TAG_NAME, "form")
            captcha_form.submit()
            time.sleep(5)
        except:
            return

    def calc_points(self):
        try:
            pirateFortress = self.chrome_driver.find_element(
                "id", "pirateFortress")
            pirateHeader = pirateFortress.find_element(
                By.CLASS_NAME, "pirateHeader")
            capturePoints = pirateHeader.find_element(
                By.CLASS_NAME, "capturePoints")
            pirateCrew = pirateHeader.find_element(
                By.CLASS_NAME, "pirateCrew")
            piracy = capturePoints.find_element(By.CLASS_NAME, "value")
            crew = pirateCrew.find_elements(By.CLASS_NAME, "value")[5]
            self.pointsSignal.emit(piracy.get_attribute(
                'innerHTML'), crew.get_attribute('innerHTML'))
        except:
            return

    def check_if_exist(self, id):
        try:
            self.chrome_driver.find_element(
                "id", id)
            return True
        except:
            return False

    def get_collect_type(self):
        if self.m_type < 2:
            return self.m_type
        return random.randrange(2)

    def select_tabmenu(self, tab):
        print('find tabmenu')
        tabmenu = self.find_element(By.CLASS_NAME, "tabmenu")
        if tabmenu == None:
            return
        print('select tab')
        tab = self.find_elements_children(tabmenu, By.TAG_NAME, "li", tab)
        if tab == None:
            return
        self.chrome_driver.execute_script(
            "arguments[0].click();", tab)
        time.sleep(3)

    def collect(self):
        # self.select_tabmenu(0)
        self.open_fortress_if_not_exist()
        self.solve_captcha_if_exist()
        if self.check_if_exist("missionProgressTime"):
            return
        print('start collect')

        pirateCaptureBox = self.find_element("id", "pirateCaptureBox")
        if pirateCaptureBox == None:
            return
        try:
            print('click abordar button')
            abordarButton = pirateCaptureBox.find_elements(
                By.TAG_NAME, "tbody")[0]
            abordarButton = abordarButton.find_elements(By.TAG_NAME, "tr")[
                self.get_collect_type()]
            abordarButton = abordarButton.find_elements(By.TAG_NAME, "td")[4]
            abordarButton = abordarButton.find_elements(By.TAG_NAME, "a")[0]
            self.sleep_random()
            self.chrome_driver.execute_script(
                "arguments[0].click();", abordarButton)
            time.sleep(5)
        except:
            return

    def train(self, number):
        try:
            print('start train')
            self.select_tabmenu(1)
            CPToCrewInput = self.chrome_driver.find_element(
                "id", "CPToCrewInput")
            CPToCrewInput.send_keys(str(number))
            time.sleep(1)
            CPToCrewSubmit = self.chrome_driver.find_element(
                "id", "CPToCrewSubmit")
            self.chrome_driver.execute_script(
                "arguments[0].click();", CPToCrewSubmit)
            time.sleep(3)
            self.select_tabmenu(0)
            print('finish train')
        except:
            return

    def attack(self, username):
        try:
            print('view island')
            viewIsland = self.find_element(
                "id", "js_islandLink")
            viewIsland_button = self.find_element_children(
                viewIsland, By.TAG_NAME, "a")
            self.chrome_driver.execute_script(
                "arguments[0].click();", viewIsland_button)
            time.sleep(3)

            updateBackgroundData = None
            while True:
                scripts = self.chrome_driver.find_elements(
                    By.TAG_NAME, "script")
                for script in scripts:
                    script = script.get_attribute('innerHTML')
                    if "updateBackgroundData" in script:
                        updateBackgroundData = script
                        break
                if updateBackgroundData != None:
                    break
            cityId = None
            if updateBackgroundData != None:
                _s = updateBackgroundData
                _s = _s[_s.index('[['):]
                _s = _s[:_s.rfind(']]') + 2]
                _s = json.loads(_s)
                cities = _s[0][1]["cities"]
                for city in cities:
                    if city['ownerName'] == username:
                        cityId = city['id']
                        break
            while cityId != None:
                _xpath = "//a[contains(@href, " + str(cityId) + ")]"
                print(_xpath)
                city = self.find_element(
                    "xpath", _xpath)
                print('open target city')
                self.chrome_driver.execute_script(
                    "arguments[0].click();", city)
                print('find cityactions')
                cityactions = self.find_element(
                    By.CLASS_NAME, "cityactions")
                print('click incursion')
                piracyRaid = None
                try:
                    piracyRaid = cityactions.find_element(
                        By.CSS_SELECTOR, "li[class='piracyRaid']")
                except:
                    self.chrome_driver.refresh()
                    time.sleep(5)
                    continue
                print('incursion found')
                piracyRaid = self.find_element_children(
                    piracyRaid, By.TAG_NAME, "a")
                self.chrome_driver.execute_script(
                    "arguments[0].click();", piracyRaid)
                time.sleep(3)
                print('click actionLink')
                actionLink = self.find_element("id", "actionLink")
                self.chrome_driver.execute_script(
                    "arguments[0].click();", actionLink)
                time.sleep(3)
                break
        except:
            pass
        try:
            print('view city')
            viewCity = self.find_element(
                "id", "js_cityLink")
            viewCity_button = self.find_element_children(
                viewCity, By.TAG_NAME, "a")
            self.chrome_driver.execute_script(
                "arguments[0].click();", viewCity_button)
            time.sleep(3)
        except:
            return

    def run(self):
        self.statusSignal.emit('Opening browser...')
        self.chrome_driver = init_chrome_driver(self.m_proxy, self.m_test)

        if self.m_test == True:
            while self.m_isRunning == True and self.chrome_available():
                time.sleep(1)
            self.chrome_driver.quit()
            return

        if self.login_game() == False:
            self.chrome_driver.quit()
            return
        if self.enter_arena() == False:
            self.chrome_driver.quit()
            return
        self.hide()

        self.statusSignal.emit('Take your actions')

        while self.m_isRunning == True and self.chrome_available():
            self.close_popup_if_exist()
            self.calc_points()

            if self.m_isPaused == False:
                self.collect()
            time.sleep(1)

        self.chrome_driver.quit()

    def startTest(self, proxy):
        if self.m_isRunning == True:
            return
        self.m_isRunning = True
        self.m_test = True
        self.m_proxy = proxy
        self.start()

    def startBot(self, username, password, proxy, type):
        if self.m_isRunning == True:
            return
        self.m_isPaused = False
        self.m_isRunning = True
        self.m_test = False
        self.m_username = username
        self.m_password = password
        self.m_proxy = proxy
        self.m_type = type
        self.start()

    def stop(self):
        if self.m_isRunning == False:
            return
        self.m_isRunning = False
        self.wait()
        self.terminate()

    def show(self):
        if self.chrome_available() == True:
            self.chrome_driver.minimize_window()
            self.chrome_driver.set_window_position(0, 0)

    def hide(self):
        if self.chrome_available() == True:
            self.chrome_driver.set_window_position(-10000, 0)

    def pause(self):
        self.m_isPaused = True

    def resume(self):
        self.m_isPaused = False
