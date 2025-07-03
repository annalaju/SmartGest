from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import subprocess
import os, cv2, time
from gesture_customization import store_gesture, extract_frames, extract_keypoints, retrain_existing_svm

app = Flask(__name__)
app.secret_key = 'random_secret_key'  # For flash messages


# Home Page
@app.route('/')
def home():
    return render_template('home.html')


# Gesture Manual Pages
@app.route('/gesture_manual')
def gesture_manual():
    return render_template('gesture_manual.html')


@app.route('/gesture_manuel2')
def gesture_manuel2():
    return render_template('gesture_manuel2.html')


# Start Gesture Recognition
@app.route('/start_gesture')
def start_gesture():
    try:
        subprocess.Popen(["python", "real_time_gesture_recognition.py"])
        return jsonify({"status": "success", "message": "Gesture recognition started"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Add Gesture Page
@app.route('/add_gesture', methods=['GET', 'POST'])
def add_gesture():
    if request.method == 'POST':
        gesture_name = request.form['gesture_name']
        gesture_action = request.form['gesture_action']
        gesture_shortcut = request.form['gesture_shortcut']

        # Save to TinyDB
        store_gesture(gesture_name, gesture_action, gesture_shortcut, "none")


        # Save to session
        session['gesture_name'] = gesture_name

        flash(f'Gesture "{gesture_name}" saved! Proceed to record.')

        # Redirect to the gesture recording page
        return redirect(url_for('gesture_record'))

    # For GET request, just render the form
    return render_template('add_gesture.html')

# Record Gesture Page
@app.route('/gesture_record')
def gesture_record():
    return render_template('gesture_record.html')


@app.route('/start_recording', methods=['POST'])
def start_recording():
    try:
        gesture_name = session.get('gesture_name', 'default_gesture')
        duration = 21  # seconds
        video_path = f'static/gesture_dataset/{gesture_name}/{gesture_name}.avi'

        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

        start_time = time.time()

        while int(time.time() - start_time) < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Extract frames
        gesture_folder = f'static/gesture_dataset/{gesture_name}'
        video_path = os.path.join(gesture_folder, f'{gesture_name}.avi')

# No extra frames folder needed
        extract_frames(video_path, gesture_name)



        # Retrain model
        retrain_existing_svm()

        return jsonify({'status': 'success', 'message': 'Recording done, Keypoints extracted, Model retrained!'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# Voice Manual Page
@app.route('/voice_maual')
def voice_maual():
    return render_template('voice_maual.html')


# Start Voice Recognition
@app.route('/start_voice')
def start_voice():
    try:
        subprocess.Popen(["python", "real_time_voice_recognition.py"])
        return jsonify({"status": "success", "message": "Voice recognition started"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Voice Command Table
@app.route('/voice_table')
def voice_table():
    voice_commands = {
        "Play": "Plays media",
        "Pause": "Pauses media",
        "Increase Volume": "Increases the volume",
        "Decrease Volume": "Decreases the volume",
        "Go Back": "Go back a few seconds",
        "Go Forward": "Go forward a few seconds",
        "Full Screen": "Enters full screen",
        "Mute": "Mutes the media",
        "Close": "Closes the player",
        "Open app <appname>": "Opens the application",
        "Sing <songname>": "Plays the song in YouTube",
    }
    return render_template('voice_table.html', voice_commands=voice_commands)

if __name__ == '__main__':
    app.run(debug=True)
