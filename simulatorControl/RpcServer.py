# coding=utf8
import os
import time, datetime
import win32gui
from PIL import ImageGrab
import shutil
from xmlrpc.server import SimpleXMLRPCServer
from simulator import Simulator

def getRpcServerStatus():
    return "running"

def simulatorStatus():
    return "running"

def runScript():
    return True


def send2web(pic_path):
    try:
        shutil.copyfile('../static/AppSimulator/images/capture.png',
                        '../static/AppSimulator/images/capture_before.png')
        shutil.copyfile(pic_path, '../static/AppSimulator/images/capture.png')
    except Exception as e:
        print("[rpc_server] send2web err", e)

    return True

def run_captrue():
    print("[rpc_server] run_captrue")
    while (1):
        capture('douyin0')
        time.sleep(5)


def capture(app_name):
    hwnd = win32gui.FindWindow(None, app_name)
    if hwnd:
        win32gui.SetForegroundWindow(hwnd)
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        app_bg_box = (left, top, right, bottom)
        im = ImageGrab.grab(app_bg_box)
        im.save('images/capture.png')
        send2web('images/capture.png')
    else:
        send2web('images/offline.jpeg')


def restartDevice(deviceId):
    print("[rpc_server] restartDevice")
    # print("Nox.exe -quit :", p.read())
    while (1):
        time.sleep(2)
        p = os.popen('tasklist /v | findstr "douyin0"')
        msg = p.read()
        print('[rpc_server] tasklist /v | findstr "douyin0"\n', msg) # tasklist /fi "imagename eq Nox.exe"
        if len(msg) > 0:
            print("[rpc_server] 模拟器正在 运行 ...")
            os.popen("C:\\Nox\\bin\\Nox.exe -quit")
            # os.popen("taskkill /f /t /im Nox.exe")
            # os.popen("taskkill /f /t /im NoxVMSVC.exe")
            # os.popen("taskkill /f /t /im NoxVMHandle.exe")
        else:
            print("[rpc_server] 将重启模拟器 ...")
            p = os.popen("C:\\Nox\\bin\\Nox.exe")
            # msg = p.read() # 不能使用 会将命令阻塞
            break

    return True


def setDeviceGPS(deviceId, latitude, longitude):
    print(deviceId, latitude, longitude)  # 39.6099202570, 118.1799316404
    p = os.popen("[rpc_server] adb shell setprop persist.nox.gps.latitude " + latitude)
    print(p.read())

    p = os.popen("[rpc_server] adb shell setprop persist.nox.gps.longitude " + longitude)
    print(p.read())
    return True


######################################################################
# netstat -ano | findstr "8003"
server = SimpleXMLRPCServer(("0.0.0.0", 8003))
server.register_function(restartDevice, "restartDevice")
server.register_function(setDeviceGPS, 'setDeviceGPS')
server.register_function(runScript, "runScript")
server.register_function(getRpcServerStatus, "getRpcServerStatus")
server.register_function(simulatorStatus, "simulatorStatus")
# server.register_function(quitApp, "quitApp")
print("[rpc_server] start ...")
server.serve_forever()
