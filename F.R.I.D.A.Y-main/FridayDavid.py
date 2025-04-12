import tkinter as tk
from tkinter import Canvas
import threading
import time
import math
import random
import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
import requests
import playsound
import pyjokes
import geocoder
import pyautogui
import cv2
import pywhatkit as kit
import instaloader
from youtube_search import YoutubeSearch
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Constants and Configuration
wakeWords = ["hey jarvis", "ok jarvis", "you there jarvis", "wake up jarvis", "hai jarvis", "jarvis are you up", "you up jarvis"]
shutdownWords = ["shutdown", "power off", "back to sleep", "go to sleep", "exit", "quit"]
wikiWords = ["wikipedia", "according to wikipedia", "search wikipedia for", "who is", "tell me about"]
searchGoogle = ["search google", "find in google"]
findLocation = ["find location", "find this location", "locate a place", "find a location", "locate this place", "find this place"]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
weatherCheck = ["get weather", "what is the weather", "check weather", "weather information", "wetaher details", "how is the weather"]
yesWords = ["yeah", "ok", "yes", "go on", "fine", "yup", "go for it"]
noWords = ["no", "no need", "naco", "nope", "nop", "not now"]
musicWords = ["sing a song", "music friday", "i am feeling groovy"]

# Browser Configuration
edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))

# Speech Engine Configuration
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

class GUI:
    instance = None

    def __init__(self, root):
        GUI.instance = self
        self.root = root
        self.root.title("JARVIS Core")
        self.root.geometry("800x800")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)
        self.root.attributes("-alpha", 0.95)

        # Canvas
        self.canvas = Canvas(root, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Animation variables
        self.state = "idle"
        self.angle1 = 0
        self.angle2 = 0
        self.pulse = 0
        self.particles = []
        self.hindi_mode = False

        # Colors
        self.core_color = "#00d4ff"
        self.glow_color = "#0077b6"
        self.particle_color = "#ffffff"
        self.accent_color = "#4dabf7"

        # Particle settings
        self.max_particles = 20

        # Start animations and assistant
        self.animate()
        threading.Thread(target=self.startup, daemon=True).start()
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def set_state(self, state):
        self.state = state

    def animate(self):
        self.canvas.delete("all")
        cx, cy = 400, 400  # Center
        self.angle1 = (self.angle1 + (6 if self.state == "listening" else 3)) % 360
        self.angle2 = (self.angle2 + (4 if self.state == "listening" else 2)) % 360
        self.pulse = (self.pulse + 0.15) % (2 * math.pi)

        # Background gradient with sparkles
        for i in range(100):
            r = 800 - i * 8
            color = f"#{'{:02x}'.format(int(5 + i * 0.3))}{'{:02x}'.format(int(10 + i * 0.3))}{'{:02x}'.format(int(20 + i * 0.5))}"
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="", fill=color)
        if random.random() < 0.05:
            x = random.randint(0, 800)
            y = random.randint(0, 800)
            self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#ffffff", outline="")

        # Holographic outer rings
        for r in [180, 170, 160]:
            speed = 6 if r == 180 else 4 if r == 170 else 2
            start = (self.angle1 if r == 180 else self.angle2) + (r % 3) * 120
            for i in range(4):
                angle = start + i * 90
                self.canvas.create_arc(
                    cx - r, cy - r, cx + r, cy + r,
                    start=angle, extent=45,
                    outline=self.glow_color if r == 180 else self.accent_color,
                    width=2 if r == 180 else 1,
                    style="arc"
                )

        # Inner core
        core_radius = 120 + 15 * math.sin(self.pulse) if self.state in ["listening", "speaking"] else 120
        self.canvas.create_oval(
            cx - core_radius, cy - core_radius, cx + core_radius, cy + core_radius,
            fill=self.core_color, outline=""
        )

        # Glow effect
        for i in range(8):
            glow_r = core_radius + i * 6
            factor = 1 - (i / 8)
            r = int(0 * factor)
            g = int(212 * factor)
            b = int(255 * factor)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_oval(
                cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                outline="", fill=color
            )

        # Processing spirals
        if self.state == "processing":
            for i in range(3):
                r = 140 + i * 10
                angle = self.angle1 + i * 120
                self.canvas.create_arc(
                    cx - r, cy - r, cx + r, cy + r,
                    start=angle, extent=60,
                    outline=self.accent_color, width=1, style="arc"
                )

        # Speaking pulses
        if self.state == "speaking":
            pulse_r = 150 + 20 * math.sin(self.pulse * 4)
            self.canvas.create_oval(
                cx - pulse_r, cy - pulse_r, cx + pulse_r, cy + pulse_r,
                outline=self.core_color, width=3
            )

        # Circuit pattern
        if self.state in ["processing", "listening"]:
            for i in range(6):
                r = 130 + i * 5
                angle = self.angle2 + i * 60
                x1 = cx + r * math.cos(math.radians(angle))
                y1 = cy + r * math.sin(math.radians(angle))
                x2 = cx + r * math.cos(math.radians(angle + 30))
                y2 = cy + r * math.sin(math.radians(angle + 30))
                self.canvas.create_line(x1, y1, x2, y2, fill=self.glow_color, width=1)

        # Particle system
        if len(self.particles) < self.max_particles:
            if self.state == "idle" and random.random() < 0.2:
                angle = random.uniform(0, 2 * math.pi)
                dist = 200
                speed = random.uniform(0.5, 1)
                size = random.uniform(2, 4)
                self.particles.append([angle, dist, speed, size, "dot"])
            elif self.state == "listening" and random.random() < 0.3:
                angle = random.uniform(0, 2 * math.pi)
                dist = 200
                speed = random.uniform(1, 2)
                size = random.uniform(3, 5)
                self.particles.append([angle, dist, speed, size, "dot"])
            elif self.state == "speaking" and random.random() < 0.4:
                angle = random.uniform(0, 2 * math.pi)
                dist = 120
                speed = random.uniform(2, 3)
                size = random.uniform(4, 6)
                self.particles.append([angle, dist, speed, size, "orb"])
            elif self.state == "processing" and random.random() < 0.3:
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(120, 200)
                speed = random.uniform(1, 3)
                size = random.uniform(2, 5)
                self.particles.append([angle, dist, speed, size, "dot"])

        for p in self.particles[:]:
            if self.state == "listening":
                p[1] -= p[2]
                p[0] += 0.05
            elif self.state == "speaking" and p[4] == "orb":
                p[1] += p[2]
                p[3] *= 0.95
            elif self.state == "processing":
                p[0] += random.uniform(-0.1, 0.1)
                p[1] += p[2] * random.choice([-1, 1])
            else:
                p[0] += 0.03
                p[1] -= 0.5

            if p[1] < 100 and self.state == "listening":
                self.particles.remove(p)
                continue
            if p[1] > 250 or p[3] < 1 or p[1] < 50:
                self.particles.remove(p)
                continue

            x = cx + p[1] * math.cos(p[0])
            y = cy + p[1] * math.sin(p[0])
            color = self.particle_color if p[4] == "dot" else self.accent_color
            self.canvas.create_oval(
                x - p[3], y - p[3], x + p[3], y + p[3],
                fill=color, outline=""
            )

        self.root.after(33, self.animate)

    def startup(self):
        WishMe()

    def listen_loop(self):
        while True:
            query = TakeCommandHindi() if self.hindi_mode else TakeCommand()
            if query:
                self.set_state("processing")
                threading.Thread(target=execute_command, args=(query.lower(),), daemon=True).start()

def Speak(audio):
    print("Friday: " + audio)
    if hasattr(GUI, 'instance') and GUI.instance:
        GUI.instance.set_state("speaking")
    engine.say(audio)
    engine.runAndWait()
    if hasattr(GUI, 'instance') and GUI.instance:
        GUI.instance.set_state("idle")

def SpeakHindi(audio):
    print("Friday (Hindi): " + audio)
    if hasattr(GUI, 'instance') and GUI.instance:
        GUI.instance.set_state("speaking")
    engine.setProperty("voice", voices[0].id)
    engine.say(audio)
    engine.runAndWait()
    if hasattr(GUI, 'instance') and GUI.instance:
        GUI.instance.set_state("idle")

def TakeCommand():
    r = sr.Recognizer()
    r.energy_threshold = 275
    with sr.Microphone() as source:
        print("Listening Boss...")
        if hasattr(GUI, 'instance') and GUI.instance:
            GUI.instance.set_state("listening")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language="en-US")
        print(f"Boss: {query}\n")
        return query
    except Exception:
        print("Sorry I didn't catch that boss")
        return ""
    finally:
        if hasattr(GUI, 'instance') and GUI.instance:
            GUI.instance.set_state("idle")

def TakeCommandHindi():
    r = sr.Recognizer()
    r.energy_threshold = 275
    with sr.Microphone() as source:
        print("Listening Boss (Hindi)...")
        if hasattr(GUI, 'instance') and GUI.instance:
            GUI.instance.set_state("listening")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language="hi-IN")
        print(f"Boss (Hindi): {query}\n")
        return query
    except Exception:
        print("माफ़ कीजिये, मैं समझ नहीं पाया।")
        return ""
    finally:
        if hasattr(GUI, 'instance') and GUI.instance:
            GUI.instance.set_state("idle")

def WishMe():
    Speak("Initializing all systems")
    try:
        playsound.playsound("D:\\F.R.I.D.A.Y-main\\F.R.I.D.A.Y-main\\FridayBoot.mp3")
    except Exception:
        Speak("Boot sound unavailable, proceeding.")
    time.sleep(2)
    Speak("All systems loaded")
    Speak("I have indeed been uploaded sir. We're on-line and ready.")
    currentDay = datetime.datetime.now().strftime("%a, %b %d, %Y")
    Speak("Today is " + str(currentDay))
    strTime = datetime.datetime.now().strftime("%I:%M %p")
    Speak(f"It is {strTime}")
    hour = int(datetime.datetime.now().hour)
    if 4 <= hour < 12:
        Speak("Good Morning boss!")
    elif 12 <= hour < 18:
        Speak("Good Afternoon boss!")
    elif 18 <= hour < 22:
        Speak("Good Evening boss")
    else:
        Speak("Good evening boss, or, should I say good night!")

def GetWeather(city="Dehradun"):
    try:
        wquery = "q=" + city
        res = requests.get('http://api.openweathermap.org/data/2.5/weather?' + wquery + '&APPID=6efd2ff32715ec6f8058f256c6535fec&units=metric')
        result = res.json()
        tempStr = f"The temperature in {city} as of now is {result['main']['temp']} degree celsius"
        tempStr2 = f"But it may vary between {result['main']['temp_min']} degree celsius and {result['main']['temp_max']} degree celsius"
        weatherStr = "Weather : " + str(result["weather"][0]["description"])
        windSpeedStr = f"The wind speed is {result['wind']['speed']} metre per second"
        humidityStr = f"The humidity is {result['main']['humidity']}"
        Speak(tempStr)
        if result["main"]["temp_min"] != result["main"]["temp_max"]:
            Speak(tempStr2)
        Speak(weatherStr)
        Speak(windSpeedStr)
        Speak(humidityStr)
    except Exception:
        Speak("Sorry boss but this location seems to be off the map")
        Speak("Would you like me to search the web boss?")
        answer = TakeCommand().lower()
        if any(phrase in answer for phrase in yesWords):
            url = f"https://google.com/search?q={city}+weather"
            webbrowser.get("edge").open_new_tab(url)
            Speak("This is what I found boss")

def CheckPendingEmails():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    try:
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', q='is:unread').execute()
        messages = results.get('messages', [])
        if not messages:
            Speak("No unread emails in your inbox, boss.")
        else:
            email_count = len(messages)
            Speak(f"You have {email_count} unread email{'s' if email_count != 1 else ''} in your inbox, boss.")
            Speak("Would you like to hear about the latest ones?")
            answer = TakeCommand().lower()
            if any(word in answer for word in yesWords):
                for message in messages[:min(3, len(messages))]:
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    headers = msg['payload']['headers']
                    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                    from_ = next(header['value'] for header in headers if header['name'] == 'From')
                    Speak(f"Email from {from_} with subject: {subject}")
    except Exception as e:
        Speak("Sorry boss, I couldn't check your emails right now.")
        print(f"Email check error: {str(e)}")

def news():
    main_url = "https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=aed16a79b07249b3ae60f2456a88b243"
    try:
        main_page = requests.get(main_url).json()
        articles = main_page['articles']
        head = []
        day = ["First", "Second", "Third", "Fourth", "Fifth"]
        for ar in articles:
            head.append(ar['title'])
        for i in range(len(day)):
            Speak(f"{day[i]} headline: {head[i]}")
    except Exception:
        Speak("Sorry boss, I couldn't fetch the news right now.")

def call_mummy():
    mummy_number = ""  # Replace with actual number
    try:
        kit.sendwhatmsg_instantly(mummy_number, "Hi Mummy! Just wanted to say I love you!", 15, True, 5)
        Speak("Sure, I've called Mummy!")
    except Exception:
        Speak("Sorry boss, I couldn't make the call right now.")

def SetAlarm(alarm_time_str):
    try:
        alarm_time = datetime.datetime.strptime(alarm_time_str, "%I:%M %p")
        current_date = datetime.datetime.now().date()
        alarm_datetime = datetime.datetime.combine(current_date, alarm_time.time())
        if alarm_datetime < datetime.datetime.now():
            alarm_datetime += datetime.timedelta(days=1)
        def alarm_thread():
            while True:
                current_time = datetime.datetime.now()
                time_difference = (alarm_datetime - current_time).total_seconds()
                if time_difference <= 0:
                    Speak("Alarm time, boss! Wake up!")
                    try:
                        playsound.playsound("D:\\F.R.I.D.A.Y-main\\F.R.I.D.A.Y-main\\FridayBoot.mp3")
                    except Exception:
                        Speak("Alarm sound unavailable.")
                    break
                time.sleep(60)
        threading.Thread(target=alarm_thread, daemon=True).start()
        Speak(f"Alarm set for {alarm_time_str}, boss.")
    except ValueError:
        Speak("Sorry boss, I couldn't understand that time format. Please use something like '3:30 PM'")

def openCamera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        Speak("Sorry boss, I couldn't access the camera.")
        return
    Speak("Camera opened. Press 'q' to close it.")
    while True:
        ret, img = cap.read()
        if not ret:
            Speak("Failed to capture image from camera.")
            break
        cv2.imshow('Camera', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    Speak("Camera closed, boss.")

def handle_wikipedia(query, phrase):
    Speak("Hang on for a second sir...")
    query_clean = query.replace(phrase, "").strip()
    if not query_clean:
        Speak("Sorry boss, I didn't catch what you want to search for.")
        return

    # Ask for detail level
    Speak("Would you like a brief or detailed summary, boss?")
    detail = TakeCommand().lower()
    sentences = 1 if "brief" in detail else 5 if "detailed" in detail else 2

    try:
        # Try to fetch Wikipedia summary
        wikipedia.set_lang("en")
        results = wikipedia.summary(query_clean, sentences=sentences, auto_suggest=False)
        Speak(results)

        # Ask for more details
        Speak("Would you like more details from Wikipedia or a web search, boss?")
        answer = TakeCommand().lower()
        if "more" in answer or "details" in answer:
            extra_sentences = wikipedia.summary(query_clean, sentences=sentences + 3)
            Speak(extra_sentences[sentences:])  # Read additional content
        elif "web" in answer or "search" in answer:
            url = f"https://google.com/search?q={query_clean}"
            webbrowser.get("edge").open_new_tab(url)
            Speak("This is what I found on the web, boss")

    except wikipedia.exceptions.DisambiguationError as e:
        Speak(f"Sir, '{query_clean}' could refer to multiple things. Here are some options.")
        options = e.options[:3]  # Limit to 3 for brevity
        for i, opt in enumerate(options, 1):
            Speak(f"Option {i}: {opt}")
        Speak("Which one would you like, boss? Say the number or name.")
        choice = TakeCommand().lower()
        selected = None
        for i, opt in enumerate(options, 1):
            if str(i) in choice or opt.lower() in choice:
                selected = opt
                break
        if selected:
            results = wikipedia.summary(selected, sentences=sentences)
            Speak(results)
        else:
            Speak("Sorry boss, I didn't catch that. Want to try a web search instead?")
            if any(word in TakeCommand().lower() for word in yesWords):
                url = f"https://google.com/search?q={query_clean}"
                webbrowser.get("edge").open_new_tab(url)
                Speak("This is what I found, boss")

    except wikipedia.exceptions.PageError:
        # Try auto-suggest
        suggested = wikipedia.search(query_clean, results=1)
        if suggested:
            Speak(f"Sorry boss, I couldn't find '{query_clean}'. Did you mean '{suggested[0]}'?")
            if any(word in TakeCommand().lower() for word in yesWords):
                results = wikipedia.summary(suggested[0], sentences=sentences)
                Speak(results)
            else:
                Speak("Would you like me to search the web instead?")
                if any(word in TakeCommand().lower() for word in yesWords):
                    url = f"https://google.com/search?q={query_clean}"
                    webbrowser.get("edge").open_new_tab(url)
                    Speak("This is what I found, boss")
                else:
                    Speak("Alright boss")
        else:
            Speak("No matches found in Wikipedia. Want to search the web?")
            if any(word in TakeCommand().lower() for word in yesWords):
                url = f"https://google.com/search?q={query_clean}"
                webbrowser.get("edge").open_new_tab(url)
                Speak("This is what I found, boss")
            else:
                Speak("Alright boss")

    except requests.exceptions.RequestException:
        Speak("Sorry boss, I'm having trouble connecting to Wikipedia right now.")
        Speak("Would you like me to search the web instead?")
        if any(word in TakeCommand().lower() for word in yesWords):
            url = f"https://google.com/search?q={query_clean}"
            webbrowser.get("edge").open_new_tab(url)
            Speak("This is what I found, boss")
        else:
            Speak("Alright boss")

def execute_command(query):
    if hasattr(GUI, 'instance') and GUI.instance:
        GUI.instance.set_state("processing")

    # Shutdown
    if any(phrase in query for phrase in shutdownWords):
        Speak("It's been a pleasure serving you boss.")
        Speak("Initializing shutdown sequence.")
        try:
            playsound.playsound("D:\\Coding\\Python\\Projects\\Virtual_Assistant_Version_1.0\\HUD Activation Sound Effect.mp3")
        except Exception:
            Speak("Shutdown sound unavailable.")
        Speak("All systems offline sir")
        if hasattr(GUI, 'instance') and GUI.instance:
            GUI.instance.root.quit()
        return

    # Wikipedia
    for phrase in wikiWords:
        if phrase in query:
            handle_wikipedia(query, phrase)
            break

    # Wake Up
    if "wake up" in query or "are you there" in query or "are you up" in query:
        try:
            playsound.playsound("D:\\F.R.I.D.A.Y-main\\F.R.I.D.A.Y-main\\jarvis-tts-file.mp3")
        except Exception:
            Speak("Wake up sound unavailable.")

    # Time
    if "the time" in query:
        strTime = datetime.datetime.now().strftime("%I:%M:%S %p")
        Speak(f"It is {strTime} boss")

    # Introduce
    if "introduce yourself" in query:
        Speak("Hello everyone, I am Jarvis, a virtual assistant created by Master Ayush.")
        Speak("I am here to assist you with various tasks and make your life easier.")
        Speak("I can help you with information, reminders, and much more.")
        Speak("Feel free to ask me anything!")

    # Open YouTube
    if "open youtube" in query:
        Speak("Just a second sir")
        webbrowser.get('edge').open_new_tab("youtube.com")
        Speak("And yup. There you go sir")

    # Speak Hindi
    if "speak in hindi" in query:
        Speak("बिलकुल सर, मैं हिंदी में बोल सकता हूँ।")
        SpeakHindi("आपका दिन शुभ हो!")
        if hasattr(GUI, 'instance') and GUI.instance:
            GUI.instance.hindi_mode = True

    # Open Google
    if "open google" in query:
        Speak("Well don't we all just love google? Just a second sir")
        webbrowser.get('edge').open_new_tab("google.com")
        Speak("Search away boss")

    # Open Spotify
    if "open spotify" in query:
        Speak("Just a second sir")
        webbrowser.get('edge').open_new_tab("spotify.com")
        Speak("And there you go boss")

    # Switch Window
    if "switch the window" in query:
        pyautogui.keyDown("alt")
        pyautogui.press("tab")
        time.sleep(1)
        pyautogui.keyUp("alt")

    # Tell Joke
    if "tell me a joke" in query:
        joke = pyjokes.get_joke()
        Speak(joke)
        print(joke)

    # Open Instagram
    if "open instagram" in query:
        webbrowser.open("https://www.instagram.com/")
        Speak("sir...Instagram is opened.")

    # Check Instagram Profile
    if "check instagram profile" in query or "profile on instagram" in query or "instagram profile" in query:
        Speak("Sir, please say the username of the profile you want to check.")
        name = TakeCommand().lower()
        if name:
            Speak("Here is the profile")
            webbrowser.open(f"https://www.instagram.com/{name}")
            time.sleep(5)
            Speak("Sir, would you like to download the profile picture?")
            condition = TakeCommand().lower()
            if "yes please" in condition:
                try:
                    mod = instaloader.Instaloader()
                    mod.download_profile(name, profile_pic_only=True)
                    Speak("Sir, the profile picture has been downloaded successfully.")
                except Exception:
                    Speak("Sorry boss, I couldn't download the profile picture.")
        else:
            Speak("I didn't catch the username, boss.")

    # Open Facebook
    if "open facebook" in query:
        webbrowser.open("https://www.facebook.com/")
        Speak("sir...Facebook is opened.")

    # Open Gmail
    if "open gmail" in query:
        webbrowser.open("https://www.gmail.com/")
        Speak("sir...Gmail is opened.")

    # Open ChatGPT
    if "open chatgpt" in query:
        webbrowser.open("https://chat.openai.com/")
        Speak("sir...ChatGPT is opened.")

    # Call Mummy
    if "call mummy" in query:
        call_mummy()

    # Open Camera
    if "open camera" in query:
        openCamera()

    # Open Notepad
    if "open notepad" in query:
        Speak("Accessing Notepad")
        Speak("This never gets old boss.")
        Speak("What should I write, boss?")
        content = TakeCommand()
        if content:
            with open("notepad_temp.txt", "w") as file:
                file.write(content)
            os.startfile("notepad_temp.txt")
            Speak("I have written it down for you, boss.")
        else:
            Speak("I didn't catch that, boss. Please try again.")

    # Open MS Word
    if "open ms word" in query:
        wordPath = 'C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE'
        try:
            os.startfile(wordPath)
            Speak("Accessing Microsoft Word")
            Speak("This never gets old boss.")
        except Exception:
            Speak("Sorry boss, I couldn't open Microsoft Word.")

    # Open MS Excel
    if "open ms excel" in query:
        excelPath = 'C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE'
        try:
            os.startfile(excelPath)
            Speak("Accessing Microsoft Excel")
            Speak("This never gets old boss.")
        except Exception:
            Speak("Sorry boss, I couldn't open Microsoft Excel.")

    # Open PowerPoint
    if "open power point" in query:
        powerPointPath = 'C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE'
        try:
            os.startfile(powerPointPath)
            Speak("Accessing Microsoft Power Point")
            Speak("This never gets old boss.")
        except Exception:
            Speak("Sorry boss, I couldn't open Microsoft PowerPoint.")

    # Open Edge
    if "open edge" in query:
        Speak("Just a second sir")
        webbrowser.get('edge').open_new_tab("google.com")
        Speak("And there you go boss")

    # Open Brave
    if "open brave" in query:
        Speak("Just a second sir")
        try:
            webbrowser.get('brave').open_new_tab("google.com")
            Speak("And there you go boss")
        except Exception:
            Speak("Sorry boss, I couldn't open Brave.")

    # Open Telegram
    if "open telegram" in query:
        webbrowser.open("https://web.telegram.org/")
        Speak("sir...Telegram is opened.")

    # Open Discord
    if "open discord" in query:
        webbrowser.open("https://discord.com/")
        Speak("sir...Discord is opened.")

    # News
    if "tell me the news" in query:
        Speak("Sure sir, let me fetch some news headlines for you:")
        news()

    # Open Twitter
    if "open twitter" in query:
        webbrowser.open("https://twitter.com/")
        Speak("sir...Twitter is opened.")

    # Open Reddit
    if "open reddit" in query:
        webbrowser.open("https://www.reddit.com/")
        Speak("sir...Reddit is opened.")

    # Open Quora
    if "open quora" in query:
        webbrowser.open("https://www.quora.com/")
        Speak("sir...Quora is opened.")

    # Open LinkedIn
    if "open linkedin" in query:
        webbrowser.open("https://www.linkedin.com/")
        Speak("sir...LinkedIn is opened.")

    # Open WhatsApp
    if "open whatsapp" in query:
        webbrowser.open("https://web.whatsapp.com/")
        Speak("sir...Whatsapp is opened.")

    # Open Chrome
    if "open chrome" in query:
        cpath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        try:
            os.startfile(cpath)
            Speak("Accessing Google Chrome")
            Speak("And there you go boss")
        except Exception:
            Speak("Sorry boss, I couldn't open Chrome.")

    # Open VS Code
    if "open vs code" in query:
        vsCodePath = 'C:\\Users\\Ayush\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe'
        try:
            os.startfile(vsCodePath)
            Speak("Accessing Visual Studio Code")
            Speak("Sir, are you gonna make some changes in me ?")
        except Exception:
            Speak("Sorry boss, I couldn't open VS Code.")

    # Send Message
    if "send message" in query:
        contacts = {
            "ayush": {"number": "+919457706231", "can_message": True},
            "mummy": {"number": "+919457394988", "can_message": True},
            "papa": {"number": "+91911224644", "can_message": True},
        }
        whatsapp_url = "https://web.whatsapp.com/send?phone={number}&text={message}"
        Speak("To whom would you like to send a message, boss?")
        recipient = TakeCommand().lower().strip()
        if not recipient:
            Speak("I didn't catch the name, boss. Please say it again.")
            recipient = TakeCommand().lower().strip()
        if recipient not in contacts:
            Speak("Sorry, I couldn't find that contact.")
        else:
            contact = contacts[recipient]
            if not contact["can_message"]:
                Speak(f"Messaging to {recipient.title()} is currently disabled.")
                Speak("Do you want to enable it?")
                if any(word in TakeCommand().lower() for word in yesWords):
                    contact["can_message"] = True
                    Speak(f"Messaging enabled for {recipient.title()}.")
                else:
                    Speak("Okay, messaging remains disabled.")
                    return
            Speak(f"What would you like to say to {recipient.title()}?")
            message = TakeCommand().lower().strip()
            if not message:
                Speak("No message heard. Try again?")
                if any(word in TakeCommand().lower() for word in yesWords):
                    Speak("What's your message?")
                    message = TakeCommand().lower().strip()
                else:
                    Speak("No worries, boss.")
                    return
            if message:
                url = whatsapp_url.format(number=contact["number"], message=message)
                webbrowser.get("edge").open_new_tab(url)
                Speak(f"Message prepared for {recipient.title()}. Please confirm in your browser.")

    # Python Module
    if "python module" in query:
        Speak("These python modules remind me of my source code days")
        webbrowser.get("edge").open_new_tab("pypi.org")
        Speak("As always sir, a great pleasure watching you work.")

    # Location
    if "where am i" in query or "what is my location" in query or "where i am" in query:
        Speak("wait sir...")
        try:
            g = geocoder.ip('me')
            latitude = g.latlng[0]
            longitude = g.latlng[1]
            reverse_geocode_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en"
            location_info = requests.get(reverse_geocode_url).json()
            city = location_info.get('city', 'Unknown city')
            country = location_info.get('countryName', 'Unknown country')
            Speak(f"Sir, We are currently in {city}, {country}.")
        except Exception:
            Speak("Sorry, I am unable to find your location at the moment.")

    # Music
    for phrase in musicWords:
        if phrase in query:
            Speak("Do you have anything specific in mind or do you want me to surprise you?")
            wish = TakeCommand().lower()
            if "surprise me" in wish:
                url = "https://ytroulette.com/?c=1&l=en"
                webbrowser.get("edge").open_new_tab(url)
                Speak("Alright boss")
                break
            else:
                Speak("Sorry boss but I don't think I can really sing this one")
                Speak("Would you like me to search the web boss?")
                answer = TakeCommand().lower()
                for phrase in yesWords:
                    if phrase in answer:
                        try:
                            results = YoutubeSearch(wish, max_results=3).to_dict()
                            url = "http://www.youtube.com" + results[0]["url_suffix"]
                            webbrowser.get("edge").open_new_tab(url)
                            Speak("This is what I got boss")
                        except Exception:
                            Speak("Sorry boss, I couldn't find that on YouTube.")
                        break
                Speak("Alright boss")

    # Command Prompt
    if "command prompt" in query:
        cPromptPath = 'C:\\Windows\\System32\\cmd.exe'
        try:
            os.startfile(cPromptPath)
            Speak("Accessing Commandline Prompt")
            Speak("This never gets old boss.")
        except Exception:
            Speak("Sorry boss, I couldn't open the command prompt.")

    # Who Are You
    if "who are you" in query or "hu r u" in query or "what are you" in query:
        Speak("I am Friday, a virtual assistant created by master Ayush.")
        Speak("My source code is written in python.")
        Speak("Since I am in my initial stages of development, my capabilities as of now...are quite limited.")
        Speak("But I will be glad to serve you in every way I can, within the limits of my capabilities boss.")

    # Wake Words
    for phrase in wakeWords:
        if phrase in query:
            Speak("Right here boss")

    # Google Search
    for phrase in searchGoogle:
        if phrase in query:
            Speak("What do you wanna search boss?")
            search = TakeCommand().lower()
            url = f"https://google.com/search?q={search}"
            webbrowser.get("edge").open_new_tab(url)
            Speak("This is what I found boss")

    # Find Location
    for phrase in findLocation:
        if phrase in query:
            Speak("What do you want me to locate boss?")
            search = TakeCommand().lower()
            url = f"https://google.nl/maps/place/{search}/&"
            webbrowser.get("edge").open_new_tab(url)
            Speak("This is what I got sir")

    # Month
    if "what is the month" in query:
        currentTime = datetime.datetime.now()
        Speak("It is " + months[currentTime.month - 1] + " boss")

    # Screenshot
    if "take a screenshot" in query or "take a screenshot" in query:
        Speak("Tell me a name for the file")
        name = TakeCommand().lower()
        if not name:
            name = f"screenshot_{int(time.time())}"
        time.sleep(3)
        try:
            img = pyautogui.screenshot()
            img.save(f"{name}.png")
            Speak("Screenshot saved")
        except Exception:
            Speak("Sorry boss, I couldn't take the screenshot.")

    # Year
    if "what is this year" in query:
        currentTime = datetime.datetime.now()
        Speak("It is " + str(currentTime.year) + " boss")

    # Day
    if "what is this day" in query:
        currentDay = datetime.datetime.now().strftime("%a, %b %d, %Y")
        Speak("Today is " + str(currentDay) + " boss")

    # Weather
    if "how is the weather" in query:
        GetWeather()

    for phrase in weatherCheck:
        if phrase in query:
            Speak("What is the location boss?")
            search = TakeCommand().lower()
            Speak("This is what I got boss")
            GetWeather(search)

    # YouTube Search
    if "search youtube" in query:
        Speak("What would you like to search for boss?")
        uwish = TakeCommand().lower()
        url = f"https://www.youtube.com/results?search_query={uwish}"
        webbrowser.get("edge").open_new_tab(url)
        Speak("Hang on a second boss")
        Speak("And there you go")

    if "say hello" in query or "introduce us" in query:
        Speak("Hello sir, I am JARVIS, and I am a final stage completed capstone project. My Makers are, Sudhanshu, Yuvraj and Tripathi. So sir, What do you think of me ?" )

    # Check Emails
    if "check emails" in query or "pending emails" in query or "unread emails" in query:
        Speak("Checking your Gmail inbox, boss...")
        CheckPendingEmails()

    # Wake Me
    if "wake me" in query or "wake me up jarvis" in query:
        try:
            playsound.playsound("D:\\F.R.I.D.A.Y-main\\F.R.I.D.A.Y-main\\Jarvis Wake Up Iron Man Edition.mp3")
        except Exception:
            Speak("Wake up sound unavailable.")

    # Set Alarm
    if "set alarm" in query:
        Speak("What time should I set the alarm for, boss? Please say it like '3:30 PM'")
        alarm_time = TakeCommand().lower()
        if alarm_time:
            SetAlarm(alarm_time)
        else:
            Speak("I didn't catch that time, boss. Please try again.")

    if hasattr(GUI, 'instance') and GUI.instance:
        GUI.instance.set_state("idle")

def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()