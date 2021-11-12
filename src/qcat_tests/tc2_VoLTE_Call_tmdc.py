import subprocess
import time

from appium import webdriver

DUT_MO_SERIAL = '96041FFBA0007B'
DUT_MT_SERIAL = '94KBA0090A'
DUT_MT_MSISDN = '14258295821'


def init_driver_MO(dut_MO):
    print("*****************Test2 - VoLTE MO to VoLTE MT -  Started*******************************\n")
    print("Creating MO Device Dialer App Driver")
    desired_caps = {
        "udid": dut_MO,
        "deviceName": dut_MO,
        "automationName": "UiAutomator2",
        "platformName": "Android",
        "appPackage": "com.google.android.dialer",
        "appActivity": ".extensions.GoogleDialtactsActivity",
		"newCommandTimeout": 3000
    }
    driver = webdriver.Remote(f'http://localhost:5000/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/{dut_MO}',
                              desired_caps)
    print("Created MO Device Dialer App Driver")

    return driver


def init_driver_MT(dut_MT):
    print("Creating MT Device Dialer App Driver")
    desired_caps = {
        "udid": dut_MT,
        "deviceName": dut_MT,
        "automationName": "UiAutomator2",
        "platformName": "Android",
        "appPackage": "com.google.android.dialer",
        "appActivity": ".extensions.GoogleDialtactsActivity",
		"newCommandTimeout": 3000
    }
    driver = webdriver.Remote(f'http://localhost:5000/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/{dut_MT}',
                              desired_caps)
    print("Created MT Device Dialer App Driver")
    return driver

def callingFunctionality(dut_MO_serial, dut_MT_serial, dut_MT_MSISDN):
	#Calling to Device B from Device A
    cmd = f'curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut_MO_serial}/shell -d \"am start -a android.intent.action.CALL -d tel:{dut_MT_MSISDN}\"'
    output = subprocess.getstatusoutput(cmd)
    print('Making a Call to MT Device')

	#Checking if Call is dialing or not on Device A
    cmd = f'curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut_MO_serial}/shell -d \"dumpsys telephony.registry | grep mCallState\"'

    for i in range(5):
        output = subprocess.getstatusoutput(cmd)[1]
        # print(output)

        # MO call has mCallState=2 not mCallState=1
        if 'mCallState=2' in output:
            print('Ringing...')
            break
        time.sleep(1)
        print('Checking call status...')
    else:
        raise Exception('MO device call is not dialing')
	
    cmd = f'curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut_MT_serial}/shell -d \"dumpsys telephony.registry | grep mCallState\"'

    for _ in range(10):
        output = subprocess.getstatusoutput(cmd)[1]
        # print(output)

        if 'mCallState=1' in output:
            break
        time.sleep(1)
        print('Checking if MT device is receiving the call...')
    else:
        raise Exception('MT device did not receive the call')
    
    print('Accepting the call on MT device')
    subprocess.call(f'curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut_MT_serial}/shell -d \"input keyevent 5\"', shell=True)

    cmd = f'curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut_MT_serial}/shell -d \"dumpsys telephony.registry | grep mCallState\"'
    
    for _ in range(10):
        output = subprocess.getstatusoutput(cmd)[1]
        # print(output)

        if 'mCallState=2' in output:
            print('\nCall connected...')
            break
        time.sleep(5)
        print('Checking call status ...')
    else:
        raise Exception('Call was not connected')

    time.sleep(5)
    
    print('Waiting for call to complete 60 seconds')
    cmd = f'curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut_MO_serial}/shell -d \"dumpsys telephony.registry | grep mCallState\"'
    
    print('Call is ongoing...', end='')
    for _ in range(15):
        output = subprocess.getstatusoutput(cmd)[1]
        # print(output)

        if 'mCallState=2' in output:
            print('.', end='')
        else:
            print('\nCall dropped')
            break
        time.sleep(1)
       
    # time.sleep(60)
    subprocess.call(f'curl -X POST http://localhost:5000/v1/ce3d5da3adc64f6397383bae8f11fd59bef2f941cd9e463f87dbc89ecdb04de0/adb/{dut_MO_serial}/shell -d \"input keyevent 6\"',
        shell=True)


def main(dut_MO=DUT_MO_SERIAL, dut_MT=DUT_MT_SERIAL, MSISDN_MT=DUT_MT_MSISDN):
    driver_MO = init_driver_MO(dut_MO)
    driver_MT = init_driver_MT(dut_MT)
    callingFunctionality(dut_MO, dut_MT, MSISDN_MT)
    driver_MO.quit()
    driver_MT.quit()
    print("\n*****************Test2 - VoLTE MO to VoLTE MT -Completed*******************************")


if __name__ == '__main__':
    main()
