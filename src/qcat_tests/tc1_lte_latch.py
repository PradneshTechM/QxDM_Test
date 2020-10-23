import os
import unittest
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
from subprocess import Popen, PIPE
import logging
import requests.packages.urllib3
import requests



#from driverInitialization import Driver

dut1 = '96071FFBA00043'

def init_driver():
    print("*****************Test1 - 4G Attach Procedure - Started *******************************")
    print("Test Location: Redmond")
    print("HeadSpin Hostname: proxy-us-pnw-1.headspin.io")
    print("Test Device Model: Google - Pixel4 XL")
    print(f"Creating a driver for Settings Apps on Pixel 4 Device - {dut1}")
    desired_caps = {
        "deviceName": "Pixel 4 XL",
        "udid": dut1,
        "automationName": "UiAutomator2",
        "appPackage": "com.android.settings",
        "platformName": "Android",
        #"appPackage": "com.google.android.dialer",
        #"appActivity": ".extensions.GoogleDialtactsActivity",
		"appPackage": "com.android.settings",
        "appActivity": ".homepage.SettingsHomepageActivity",
		"newCommandTimeout": 3000
    }
    driver = webdriver.Remote('https://us-pnw.headspin.io:7012/v0/4aea75eb1ac3401eb1c95c4362ff68dd/wd/hub',
                              desired_caps)
    print("Driver is created for Settings App")	
	
    #print("Driver details are as follows:")	
    #print(driver)

    network_element= WebDriverWait(driver, 30).until(
		EC.element_to_be_clickable((MobileBy.XPATH, "//*[@text=\"Network & internet\"]" ))
	)
    network_element.click()
	
    return driver


def enabled_root():
    subprocess.call(
        f"curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/{dut1}/shell -d \"root\"",
        shell=True)
    time.sleep(15)


def enable_airplane_mode():
    
    print("Turning on Airplane mode..........")
    subprocess.call(
        f"curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/{dut1}/shell -d \"settings put global airplane_mode_on 1\"",
        shell=True)

    cmd = f"curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/{dut1}/shell -d \"am broadcast -a android.intent.action.AIRPLANE_MODE\""
    status, output = subprocess.getstatusoutput(cmd)
    #print("+++++++++++************+++++" + output + "+++++++++++++**************+++")
    if (output.__contains__("Broadcast completed")):
        print("\nAirplane mode on")

    else:
        print("Error: Unable to change airplane mode to on")

    time.sleep(5)


def disable_airplane_mode():
    print("Turning off Airplane mode..........")

    subprocess.call(
        f"curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/{dut1}/shell -d \"settings put global airplane_mode_on 0\"",
        shell=True)

    cmd1 = f"curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/{dut1}/shell -d \"am broadcast -a android.intent.action.AIRPLANE_MODE\""
    status, output = subprocess.getstatusoutput(cmd1)
    #print("+++++++++++************+++++" + output + "+++++++++++++**************+++")
    if (output.__contains__("Broadcast completed")):
        print("\nAirplane mode off")

    else:
        print("Error: Unable to change airplane mode to on")


def verifyLTE():
    print("Checking if LTE is latched........")
    cmd1 = f"curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/{dut1}/shell -d \"dumpsys telephony.registry\""
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
    requests.packages.urllib3.disable_warnings()
    driver = init_driver()
    enable_airplane_mode()
    disable_airplane_mode()
    verifyLTE()
    driver.quit()
    print("*****************Test1 - 4G Attach Procedure - Completed *******************************")


if __name__ == '__main__':
    #enabled_root()
    requests.packages.urllib3.disable_warnings()
    driver = init_driver()
    enable_airplane_mode()
    disable_airplane_mode()
    verifyLTE()
    driver.quit()
    print("*****************Test1 - 4G Attach Procedure - Completed *******************************")
