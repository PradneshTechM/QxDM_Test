import subprocess
import time

from appium import webdriver


def init_driver():
    print("*****************Test2 - VoLTE MO to VoLTE MT -  Started*******************************\n")
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


def callingFunctionality():

	#Calling to Device B from Device A
    
    cmd = "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"am start -a android.intent.action.CALL -d tel:4696137553\""
    output = subprocess.getstatusoutput(cmd)
    print("Calling.................")

	#Checking if Call is dialing or not on Device A
    cmd1 = "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"dumpsys telephony.registry\""
    status, output = subprocess.getstatusoutput(cmd1)
	
    for i in range(5):
        if output.__contains__("mCallState=1"):
            print("Ringing..")
            break
        else:
            time.sleep(1)
            print("Checking call status ..........")
    # print("+++++++++++************+++++" + output + "+++++++++++++**************+++")
	
	#Checking if Device B is receiving the call
	
    print("Checking if Device B is receiving the call")
    for i in range(10):
        call_flag=0
        cmd1 = "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96031FFBA001J1/shell -d \"dumpsys telephony.registry\""
        status, output = subprocess.getstatusoutput(cmd1)
        for j in range(5):
            if output.__contains__("mCallState=1"):
                print("Device B received the Call")
				
				#Accept the call if it's ringing
                print("Accepting the call on Device B")
                subprocess.call(
                "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96031FFBA001J1/shell -d \"input keyevent 5\"", shell=True)
                call_flag=1
                break
            else:
                time.sleep(1)
                print("Checking if Device B is receivng the call..........")
        if call_flag == 1:
            break
    for i in range(10):
        cmd1 = "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96031FFBA001J1/shell -d \"dumpsys telephony.registry\""
        status, output = subprocess.getstatusoutput(cmd1)
        if output.__contains__("mCallState=2"):
            print("Call connected..")
            break
        else:
            time.sleep(5)
            print("Checking call status ..........")
    time.sleep(5)
    
    print("Waitig for call to complete 60 seconds")
    cmd1 = "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"dumpsys telephony.registry\""
    
    for i in range(15):
        status, output = subprocess.getstatusoutput(cmd1)
        print("Checking call status ..........")
        if output.__contains__("mCallState=2"):
            print("Call is not dropped")
            time.sleep(1)
        else:
            print("Call is dropped")
            break

       
    # time.sleep(60)
    subprocess.call(
        "curl -X POST https://7bfc56fb456d447e9337209c889d211e@api-dev.headspin.io/v0/adb/96071FFBA00048/shell -d \"input keyevent 6\"",
        shell=True)

def main():
    driver = init_driver()
    callingFunctionality()
    driver.quit()
    print("*****************Test2 - VoLTE MO to VoLTE MT -Completed*******************************")


if __name__ == '__main__':
    driver = init_driver()
    callingFunctionality()
    driver.quit()
    print("*****************Test2 - VoLTE MO to VoLTE MT -Completed*******************************")
