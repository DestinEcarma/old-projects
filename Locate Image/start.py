import pyautogui
import keyboard
import time
import mouse
from numpy import *

allow = True

def locateOnScreen():
    global allow

    if pyautogui.locateOnScreen('image.png') != None and allow == True:
        allow = False
        current_Mouse = mouse.get_position()
        image = pyautogui.locateOnScreen('image.png')
        pyautogui.click(image)
        mouse.move(current_Mouse[0], current_Mouse[1])
        time.sleep(0.1)
        allow = True

while keyboard.is_pressed("q") == False:
    locateOnScreen()