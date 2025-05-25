from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
import os
from gtts import gTTS
from datetime import datetime
import pytz

aest = pytz.timezone('Australia/Sydney')
now = datetime.now(aest).strftime("%Y-%m-%d %H:%M:%S")

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a new secret key on each restart

# Clear session on app restart
@app.before_request
def clear_session_on_restart():
    if 'initialized' not in session:
        session.clear()  # Clear all session data
        session['initialized'] = True  # Mark the session as initialized

# Function to get a random noun from the database
def get_random_noun():
    conn = sqlite3.connect('nouns.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, noun, gender, english, identifier_id FROM nouns ORDER BY RANDOM() LIMIT 1")
    noun = cursor.fetchone()
    conn.close()
    return {
        "id": noun[0],
        "word": noun[1],  # Updated to match the 'noun' column
        "gender": noun[2],
        "meaning": noun[3],  # Updated to match the 'english' column
        "identifier_id": noun[4]
    }

@app.route('/')
def index():
    # Initialize session variables only if they don't already exist
    if 'correct_count' not in session:
        session['correct_count'] = 0
    if 'total_count' not in session:
        session['total_count'] = 0

    noun = get_random_noun()
    # Generate the text to be s
    tts_text = f"Der {noun['word']}, oder Die {noun['word']}, oder Das {noun['word']}"
    audio_path = os.path.join('static', 'audio', 'index.mp3')
    # Remove old audio if exists
    if os.path.exists(audio_path):
        os.remove(audio_path)
    # Generate and save new audio
    tts = gTTS(tts_text, lang='de')
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    tts.save(audio_path)
    return render_template('index.html', noun=noun)



@app.route('/check', methods=['POST'])
def check():
    selected_gender = request.form.get('gender')
    correct_gender = request.form.get('correct_gender')
    noun_word = request.form.get('noun')
    identifier_id = request.form.get('identifier_id')
    meaning = request.form.get('meaning')
    noun_id = request.form.get('noun_id')

    # Fetch reason from the identifiers table
    conn = sqlite3.connect('nouns.db')
    cursor = conn.cursor()
    cursor.execute("SELECT reason FROM identifiers WHERE id = ?", (identifier_id,))
    result = cursor.fetchone()
    if result is None:
        reason = "No explanation available for this noun."
    else:
        reason = result[0]
    conn.close()

    # Update session counters
    session['total_count'] += 1
    if selected_gender == correct_gender:
        session['correct_count'] += 1
        result = "Correct!"
        color = {"der": "blue", "die": "pink", "das": "green"}[correct_gender]
    else:
        result = "Wrong answer!"
        color = "white"
        # Record the mistake
        conn = sqlite3.connect('nouns.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mistakes (noun_id, noun, correct_gender, user_answer, meaning, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (noun_id, noun_word, correct_gender, selected_gender, meaning, now)
        )
        conn.commit()
        conn.close()

    # Generate text-to-speech audio
    # Generate text-to-speech audio with pauses
    tts_text = f"{correct_gender} {noun_word} , , , , ,  {correct_gender} {noun_word} , , , , ,  {correct_gender} {noun_word}"
    audio_path = os.path.join('static', 'audio', 'result.mp3')

    # Remove the old audio file if it exists
    if os.path.exists(audio_path):
        os.remove(audio_path)

    # Generate and save the new audio file
    tts = gTTS(tts_text, lang='de')  # 'de' for German
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)  # Ensure the directory exists
    tts.save(audio_path)

    # Calculate percentage
    percentage = (session['correct_count'] / session['total_count']) * 100

    return render_template(
        'result.html',
        noun=noun_word,
        result=result,
        color=color,
        explanation=reason,
        correct_gender=correct_gender,
        meaning=meaning,
        percentage=percentage,
        audio_file=audio_path  # Pass the audio file path to the template
    )

if __name__ == '__main__':
    app.run(debug=True)