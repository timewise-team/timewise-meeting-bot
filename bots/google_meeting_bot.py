"""
This bot is to auto join google meetings and record it
Transform to text transcript
Insert text transcript to database for further analysis
"""
import os
import tempfile
import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from recording_processer.audio_recorder import AudioRecorder


class GoogleMeetBot:
    def __init__(self):
        self.mail_address = 'kid.from.past@gmail.com'
        self.password = 'Hngnhatkhanh0708'
        # create chrome instance
        opt = Options()
        opt.add_argument("/home/khanhhn.hoang/.config/google-chrome/Default")
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
        # opt.add_argument('--no-sandbox')
        # opt.add_argument('--disable-dev-shm-usage')
        # opt.add_argument('--disable-blink-features=AutomationControlled')
        # opt.add_argument('--window-size=1920,1080')
        # opt.add_argument('--disable-gpu')  # Disable GPU acceleration
        # opt.add_argument('--disable-software-rasterizer')
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        self.driver = webdriver.Chrome(options=opt)

    def go_to_meeting(self, meet_link):
        # go to google login page
        self.driver.get(meet_link)
        time.sleep(10)

        # if self.driver.find_element(By.CSS_SELECTOR, 'div[jscontroller="VXdfxd"]').is_displayed():
        #     self.driver.find_element(By.CSS_SELECTOR, 'div[jscontroller="VXdfxd"]').click()

        self.driver.find_element(By.ID, 'identifierId').send_keys(self.mail_address)
        self.driver.find_element(By.ID, "identifierNext").click()
        self.driver.implicitly_wait(10)

        self.driver.find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(self.password)
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.ID, "passwordNext").click()
        self.driver.implicitly_wait(10)
        time.sleep(5)

        print("Gmail login activity: Done")

    def turn_off_mic_cam(self):
        # time.sleep(20)
        # turn off Microphone
        self.driver.find_element(By.CSS_SELECTOR, 'div[jsname="Dg9Wp"]').click()
        self.driver.implicitly_wait(3000)
        print("Turn off mic activity: Done")

        # turn off camera
        self.driver.find_element(By.CSS_SELECTOR, 'div[jsname="R3GXJb"]').click()
        self.driver.implicitly_wait(3000)
        print("Turn off cam activity: Done")

    def join_meeting(self, audio_path, schedule_id):
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, 'button[jsname="Qx7uuf"]').click()
        print("Asking to join activity...")

        if self.check_if_joined():
            print("Meeting has been joined, start recording...")
            AudioRecorder().start_audio_recording(self, audio_path, schedule_id)
            return

        print("Meeting has not been joined")

    def check_if_joined(self):
        try:
            # Wait for the join button to appear
            _ = WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, 'button[jsname="CQylAd"]'))
            )
            return True
        except (TimeoutException, NoSuchElementException):
            print("Meeting has not been joined")
            return False

    def check_if_meeting_ended(self):
        try:
            _ = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, 'button[jsname="dqt8Pb"]'))
            )
            return True
        except (TimeoutException, NoSuchElementException):
            print("Meeting is still ongoing")
            return False