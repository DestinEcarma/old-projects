import win32api
import pyttsx3
import pdfplumber
import threading
import time

class tts:
    def __init__(self, pause):
        self.pause = pause
        
    def voice(self):
        txt = ""
        path = "test.pdf"
        speaker = pyttsx3.init()
        voices = speaker.getProperty("voices")
        speaker.setProperty("rate", 178)
        speaker.setProperty('voice', voices[1].id)

        with pdfplumber.open(path) as pdf:
            for num in range(len(pdf.pages)):
                page = pdf.pages[num]
                txt = txt + page.extract_text().replace('\n', ' ').replace('.', '.\n').replace(',', ',\n')

                for line in txt.splitlines():
                    if self.pause == False:
                        print(line + "\n")
                        speaker.say(line)
                        speaker.runAndWait()
                    else:
                        print("Press enter to continue...")
                        input()
                        self.pause = False
                        
                txt = ""

    def pauseCheck(self):
        while True:
            a = win32api.GetKeyState(0x20)
            time.sleep(1)

            if a < 0:
                self.pause = True

test = tts(False)

if __name__ == '__main__':
    threading.Thread(target=test.pauseCheck).start()
    threading.Thread(target=test.voice).start()