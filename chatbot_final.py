# If you get ALSA errors when Init the Microphone just comment out the cards.pcm.surrond etc. in:
# /usr/share/alsa/alsa.conf

# Uncomment the following to enable verbose logging
# import logging
# logging.basicConfig(level=logging.INFO)

# Use Fullscreen (True/False)
setToFullscreen = True

# Bot Name (If you chage the name be aware that the corpus data will not change)
chatbot_name = "Rob"

# Use speech output (True/False)
useSpeechOutput = True

# Use mic (Speechrecognition) (True/False)
useSpeechRecognition = True

# Use training data
useTrainingData = True

# Export learned Chatbot corpus (useTrainingData must be True to success)
exportChatbotCorpus = False

# Import Speech Recognition api
import speech_recognition as sr

# Import and config pyttsx3 -- Text to Speech Sound Output
import pyttsx3
engine = pyttsx3.init()
engine.setProperty("voice", "german") # Language
engine.setProperty("rate", 150)    # Speed percent (can go over 100)
engine.setProperty("volume", 0.9)  # Volume 0-1

# Import Chatterbot
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# Import threading for dual Mic/Keyboard input
import threading
import time

#Import tkinter as GUI manager
from tkinter import *
import tkinter as tki
from tkinter.scrolledtext import ScrolledText

# Create a new instance of a ChatBot
bot = ChatBot(
    "Terminal",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'
    ],
    logic_adapters=[
        # Look for Chatterbot API to add mor logic to the bot
        #"chatterbot.logic.UnitConversion",
        #"chatterbot.logic.TimeLogicAdapter",
        "chatterbot.logic.MathematicalEvaluation",
        "chatterbot.logic.BestMatch"

    ],
    database_uri="sqlite:///database.db" # Save Database as Mysql database
)

# Add more Training data (look for venv if doesn't find):
# /home/kai/.local/lib/python3.6/site-packages/chatterbot_corpus/data/german
if useTrainingData:
    trainer = ChatterBotCorpusTrainer(bot)
    trainer.train("chatterbot.corpus.german") # Reads data from: ~/chatterbot_corpus/data/german/*
    if exportChatbotCorpus:
        trainer.export_for_training('./export.yml')

# Create a Thread that will force focus on inp1 (Keyboard input)
class lockWindow(threading.Thread):
    def __init__(self):
        super(lockWindow, self).__init__()
        self.setDaemon(True)

    def run(self):
        while True:
            time.sleep(1.0)
            root.lift()
            inp1.focus_set()
            root.after(100, self.run())

#Create the SpeechRecognizer Thread
class SpeechRecognizer(threading.Thread):
    def __init__(self):
        super(SpeechRecognizer, self).__init__()
        self.setDaemon(True)
        self.recognized_text = "initial"

    def run(self):
        while True:
            try:
                # Use Speech Input
                r = sr.Recognizer()
                with sr.Microphone() as source:  # Every thime the Mic gets
                    #st.insert(END, "Sag etwas" "\n")
                    txt0.delete(0, END)
                    txt0.insert(END, "Höre")
                    audio = r.listen(source)
                    try:
                        txt0.delete(0, END)
                        txt0.insert(END, "Sprachverarbeitung")
                        # Coose from one of the speechrecognition api's
                        #user_input = r.recognize_sphinx(audio, language="de-de")
                        user_input = r.recognize_wit(audio, key="XZCYQRIKRFMCTEKNK5LHTDPUHIWLBWG5")
                        #user_input = r.recognize_google(audio, language="de-de")

                        txt1.insert(END, "Du: " + user_input + "\n", 'green')
                        txt1.see("end")
                        txt0.delete(0, END)
                        txt0.insert(END, "Denke")
                        bot_response = str(bot.get_response(user_input))
                        txt1.insert(END, chatbot_name + ": " + bot_response + "\n", 'red')
                        txt1.see("end")

                        if useSpeechOutput:
                            txt0.delete(0, END)
                            txt0.insert(END, "Spreche")
                            root.update() # Output text before speech
                            engine.say(bot_response)
                            engine.runAndWait()

                    except sr.UnknownValueError:
                        # Mabye here a fallback for another Speechrecognition software like wit for online...?
                        txt1.insert(END, chatbot_name + ": Entschuldigung, ich habe sie leider nicht richtig verstanden", 'red')
                        if useSpeechOutput:
                            root.update() # Output text before speech
                            engine.say("Entschuldigung, ich habe sie leider nicht richtig verstanden")
                            engine.runAndWait()

                    except sr.RequestError as e:
                        txt1.insert(END, chatbot_name + ": Es konnten keine Ergebnisse von der Sprach-API angefordert werden; {0}".format(e), 'red')
                        if useSpeechOutput:
                            root.update() # Output text before speech
                            engine.say("Es konnten keine Ergebnisse von der Sprach-API angefordert werden; {0}".format(e))
                            engine.runAndWait()

            # Press ctrl-c or ctrl-d on the keyboard to exit
            except (KeyboardInterrupt, EOFError, SystemExit):
                break

#Create the GUI Elements
class GUI(object):
    def func(event):
        user_input = str(inp1.get())
        inp1.delete(0, END)
        #Do nothing if enter is pressed
        if  not user_input.strip():
            return
        # Close app when the "code" is entered
        if user_input == "quit 123456":
            quit()
        txt1.insert(END, "Du: " + user_input + "\n", 'green')  # this insert "text" into the box \n for next row
        txt1.see("end")
        bot_response = str(bot.get_response(user_input))
        txt1.insert(END, chatbot_name + ": " + bot_response + "\n", 'red')
        txt1.see("end")
        if useSpeechOutput:
            root.update() # Output text before speech
            engine.say(bot_response)
            engine.runAndWait()
        #inp1.focus_set()

    def __init__(self,root):
        self.root = root

        # create a Frame for the Text and Scrollbar
        txt_frm = tki.Frame(self.root, width=800, height=600)
        txt_frm.pack(fill="both", expand=True)

        # Set to fullscreen if True
        if setToFullscreen:
            self.root.attributes('-fullscreen', True)

        # ensure a consistent GUI size
        txt_frm.grid_propagate(False)

        # function when enter is pressed
        self.root.bind('<Return>', GUI.func)

        #Create invitation label
        label1 = Label(self.root, text="Chatte mit mir", width=50, height=1, bg="white")
        label1.place(relx=0.5, rely=0.05, anchor=CENTER)
        label1.config(font=("Courier", 44))

        photo = PhotoImage(file="background.png")
        label2 = Label(txt_frm, image=photo)
        label2.image = photo  # keep a reference!
        label2.place(relx=0.5, rely=0.5, anchor=CENTER)


        global txt0 # textbox display thinking process
        txt0 = Entry(txt_frm, width=20, justify='center')
        txt0.place(relx=0.5, rely=0.19, anchor=CENTER)

        # Hide progress bar if no speech is not used
        if not useSpeechRecognition:
            txt0.place_forget()

        self.lbl1 = tki.Label(txt_frm, text="Chatbot - Halten sie den Knopf beim sprechen gedrückt \n oder nutzen sie die Tastatur um mit mir zu kommunizieren")
        self.lbl1.place(relx=0.5, rely=0.29, anchor=CENTER)

        global txt1 # chatbox
        txt1 = ScrolledText(txt_frm, borderwidth=3, relief="sunken", height=25,width=60)
        txt1.config(font=("consolas", 12), undo=True, wrap='word')
        txt1.place(relx=0.5, rely=0.48, anchor=CENTER)
        txt1.tag_config('green', foreground='green')
        txt1.tag_config('red', foreground='red')

        global inp1 # Inputbox for Keyboard inputs
        inp1 = Entry(txt_frm, width=77)
        inp1.place(relx=0.5, rely=0.768, anchor=CENTER)
        inp1.focus_set()

root = tki.Tk()
app = GUI(root)

#Start SpeechRecognizer Thread to support Mic and Keyboard input at the same time
if useSpeechRecognition:
    recognizer = SpeechRecognizer()
    recognizer.start()

#start the focus on inp1 thread
if setToFullscreen:
    windowLocker = lockWindow()
    windowLocker.start()

#Start GUI with mainloop
root.mainloop()
