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

DUT = '96041FFBA0007B'

def init_driver(dut):
    print("*****************Test1 - 4G Attach Procedure - Started *******************************")
    print("Test Location: Redmond")
    print("TMDC Hostname: localhost")
    print("Test Device Model: Google - Pixel4 XL")
    print(f"Creating a driver for Settings Apps on Pixel 4 Device - {dut}")

    desired_caps = {
        "udid": dut,
        "deviceName": dut,
        "automationName": "UiAutomator2",
        "appPackage": "com.android.settings",
        "platformName": "Android",
        "appActivity": ".homepage.SettingsHomepageActivity",
		"newCommandTimeout": 3000
    }
    driver = webdriver.Remote(f'http://localhost:5000/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/{dut}',
                              desired_caps)
    print("Driver is created for Settings App")	
	
    #print("Driver details are as follows:")	
    #print(driver)

    network_element= WebDriverWait(driver, 30).until(
		EC.element_to_be_clickable((MobileBy.XPATH, "//*[@text=\"Network & internet\"]" ))
	)
    network_element.click()
	
    return driver


def enabled_root(dut):
    subprocess.call(
        f"curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut}/shell -d \"root\"",
        shell=True)
    time.sleep(15)


def enable_airplane_mode(dut):
    print("Turning on Airplane mode..........")
    subprocess.call(
        f"curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut}/shell -d \"settings put global airplane_mode_on 1\"", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    cmd = f"curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut}/shell -d \"am broadcast -a android.intent.action.AIRPLANE_MODE\""
    output = subprocess.getstatusoutput(cmd)[1]
    i = 0
    while i < 10 and 'Broadcast completed' not in output:
        time.sleep(1)
        print('Checking airplane mode is turned on ...')
        output = subprocess.getstatusoutput(cmd)[1]
        i += 1
    if 'Broadcast completed' in output:
        print('Airplane mode on')
    else:
        print("Error: Unable to change airplane mode to on")


def disable_airplane_mode(dut):
    print("Turning off Airplane mode..........")
    subprocess.call(
        f"curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut}/shell -d \"settings put global airplane_mode_on 0\"", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    cmd1 = f"curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut}/shell -d \"am broadcast -a android.intent.action.AIRPLANE_MODE\""
    output = subprocess.getstatusoutput(cmd1)[1]
    i = 0
    while i < 10 and 'Broadcast completed' not in output:
        time.sleep(1)
        print('Checking airplane mode is turned off...')
        output = subprocess.getstatusoutput(cmd1)[1]
        i += 1
    if 'Broadcast completed' in output:
        print('Airplane mode off')
    else:
        print("Error: Unable to change airplane mode to on")


def verifyLTE(dut):
    print("Checking if LTE is latched........")
    cmd1 = f"curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut}/shell -d \"dumpsys telephony.registry\""
    output = subprocess.getstatusoutput(cmd1)[1]

    i = 0
    while i < 10 and 'mDataConnectionState=2' not in output:
        time.sleep(1)
        print('Checking connection status...')
        output = subprocess.getstatusoutput(cmd1)[1]
        i += 1
    if 'mDataConnectionState=2' in output:
        print('LTE Network is available')


def main(dut=DUT):
    requests.packages.urllib3.disable_warnings()
    driver = init_driver(dut)
    time.sleep(2)
    enable_airplane_mode(dut)
    time.sleep(1)
    disable_airplane_mode(dut)
    verifyLTE(dut)
    driver.quit()
    print("*****************Test1 - 4G Attach Procedure - Completed *******************************")


if __name__ == '__main__':
    #enabled_root()
    main()
