import speech_recognition as sr
import keyboard
import time
import threading
import subprocess
import webbrowser 
from tinydb import TinyDB, Query

# Load TinyDB for voice command mappings
db = TinyDB("voice_commands.json")
VoiceCommand = Query()

# Mapping of functions to keyboard shortcuts
shortcut_mappings = {
    "play": "space",
    "pause": "space",
    "increase volume": "volume up", 
    "decrease volume": "volume down",
    "go back": "left",
    "go forward": "right",
    "full screen": "f",
    "mute": "m",
    "close": "alt+f4",
}

# Mapping application names to executable files
app_mappings = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "notepad": "notepad",
    "calculator": "calc",
    "vlc": "vlc",
}

# Flag to control the recognition loop
running = True

# Function to open applications
def open_application(app_name):
    app_name = app_name.lower()
    if app_name in app_mappings:
        if app_name.lower() == "chrome":
            webbrowser.open("https://www.google.com")  # Opens Chrome with Google
            print("🚀 Opening Chrome in browser...")
        else:
            subprocess.Popen(app_mappings[app_name])
            print(f"🚀 Opening {app_name}...")
    else:
        print(f"⚠ No mapping found for '{app_name}'")

# Function to play a song on YouTube
def play_song(song_name):
    search_url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
    webbrowser.open(search_url)
    print(f"🎵 Searching for '{song_name}' on YouTube...")

# Function to recognize voice and execute commands
def recognize_and_execute():
    global running
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 Listening for voice command in background... (Say 'stop' to exit)")
        recognizer.adjust_for_ambient_noise(source)

        while running:
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                print(f"✅ Recognized command: {command}")

                # Stop recognition if the user says "stop"
                if command == "stop":
                    print("🔴 Voice recognition stopped by user command.")
                    running = False
                    break

                # Handle "open app <appname>" command
                elif command.startswith("open app"):
                    app_name = command.replace("open app", "").strip()
                    open_application(app_name)

                # Handle "sing <songname>" command
                elif command.startswith("sing"):
                    song_name = command.replace("sing", "").strip()
                    play_song(song_name)

                # Retrieve function from TinyDB
                elif command in shortcut_mappings:
                    shortcut = shortcut_mappings[command]
                    if callable(shortcut):  # If it's a function (volume control)
                        shortcut()
                    else:
                        keyboard.press_and_release(shortcut)
                    print(f"🚀 Executed: {command}")
                    time.sleep(1)  # Prevent multiple triggers

                else:
                    print("❌ Command not found in database.")

            except sr.UnknownValueError:
                print("❌ Could not understand the command.")
            except sr.RequestError:
                print("❌ Google Speech API request failed.")

# Run voice recognition in the background
def run_background():
    thread = threading.Thread(target=recognize_and_execute, daemon=True)
    thread.start()
    print("🎙 Voice recognition running in the background... (Say 'stop' to exit)")

# Start background voice recognition
run_background()

# Keep the main program running
while running:
    try:
        time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("\n🔴 Exiting...")
        running = False
        break