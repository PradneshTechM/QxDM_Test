import os
import unittest
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
from subprocess import Popen, PIPE

#from driverInitialization import Driver

dut1 = '96071FFBA00048'
dialpad_fab_ID = 'com.google.android.dialer:id/dialpad_fab'


def init_driver():
    print("*****************Test1 - 4G Attach Procedure - Started *******************************")
    desired_caps = {
        "deviceName": "Pixel 4 XL",
        "udid": "96071FFBA00048",
        "automationName": "UiAutomator2",
        "appPackage": "com.android.settings",
        "platformName": "Android",
        "appPackage": "com.google.android.dialer",
        "appActivity": ".extensions.GoogleDialtactsActivity",
		"newCommandTimeout": 3000
    }
    driver = webdriver.Remote('https://us-pnw.headspin.io:7012/v0/4aea75eb1ac3401eb1c95c4362ff68dd/wd/hub',
                              desired_caps)
    return driver


def enabled_root():
    subprocess.call(
        "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"root\"",
        shell=True)
    time.sleep(15)


def enable_airplane_mode():
    
    print("Tuning on Airplane mode..........")
    subprocess.call(
        "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"settings put global airplane_mode_on 1\"",
        shell=True)

    cmd = "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"am broadcast -a android.intent.action.AIRPLANE_MODE\""
    status, output = subprocess.getstatusoutput(cmd)
    print("+++++++++++************+++++" + output + "+++++++++++++**************+++")
    if (output.__contains__("Broadcast completed")):
        print("Airplane mode on")

    else:
        print("Error: Unable to change airplane mode to on")

    time.sleep(5)


def disable_airplane_mode():
    print("Tuning off Airplane mode..........")

    subprocess.call(
        "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"settings put global airplane_mode_on 0\"",
        shell=True)

    cmd1 = "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"am broadcast -a android.intent.action.AIRPLANE_MODE\""
    status, output = subprocess.getstatusoutput(cmd1)
    print("+++++++++++************+++++" + output + "+++++++++++++**************+++")
    if (output.__contains__("Broadcast completed")):
        print("Airplane mode on")

    else:
        print("Error: Unable to change airplane mode to on")

def verifyLTE():
    print("Checking if LTE is latched........")
    cmd1 = "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"dumpsys telephony.registry\""
    status, output = subprocess.getstatusoutput(cmd1)
    #print("+++++++++++************+++++" + output + "+++++++++++++**************+++")
    for i in range(10):
        if output.__contains__("mDataConnectionState=2"):
            print("LTE Network is available ")
            break
        else:
            time.sleep(10)
            print("Checking connection status ..........")

def main():
    driver = init_driver()
    enable_airplane_mode()
    disable_airplane_mode()
    verifyLTE()
    driver.quit()

if __name__ == '__main__':
    #enabled_root()
    driver = init_driver()
    enable_airplane_mode()
    disable_airplane_mode()
    verifyLTE()
    driver.quit()
