from flask import Flask, render_template, jsonify, request, session
import random
import json
import os
import sys

# กำหนดพาธสำหรับบันทึกสถิติ
STATISTICS_PATH = "D:/Zombitx64/Tictactoe-zombitx64/statistics"

# ตรวจสอบว่าโฟลเดอร์มีอยู่หรือไม่ ถ้าไม่มีให้สร้างใหม่
if not os.path.exists(STATISTICS_PATH):
    os.makedirs(STATISTICS_PATH)

# Add the DatasetPokerzombitx64 directory to the Python path
sys.path.append('DatasetPokerzombitx64')

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tictactoe')
def tictactoe():
    ai = request.args.get('ai', '0')
    return render_template('tictactoe.html', ai_mode=ai)

@app.route('/connect_four')
def connect_four():
    ai = request.args.get('ai', '0')
    return render_template('connect_four.html', ai_mode=ai)

@app.route('/checkers')
def checkers():
    ai = request.args.get('ai', '0')
    return render_template('checkers.html', ai_mode=ai)

@app.route('/poker')
def poker():
    """หน้าเกม Poker"""
    # สร้าง session ID ถ้ายังไม่มี
    if 'game_id' not in session:
        session['game_id'] = str(random.randint(10000, 99999))
    
    return render_template('poker.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
