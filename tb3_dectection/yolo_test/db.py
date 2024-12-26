import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# 데이터베이스 파일 생성 및 테이블 설정
def init_db():
    conn = sqlite3.connect('tracking.db')  # 데이터베이스 연결 (파일 생성)
    cursor = conn.cursor()

    # 테이블 생성 (추격 기록 저장용)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracking_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()

# 추격 버튼 눌렀을 때 시각을 기록하는 함수
def log_tracking_time():
    conn = sqlite3.connect('tracking.db')  # 데이터베이스 연결
    cursor = conn.cursor()

    # 현재 시각을 'YYYY-MM-DD HH:MM:SS' 형식으로 얻기
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 추격 기록을 데이터베이스에 삽입
    cursor.execute('INSERT INTO tracking_log (timestamp) VALUES (?)', (timestamp,))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == '1234':
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track():
    # 추격 버튼을 눌렀을 때 시각 기록
    log_tracking_time()

    # 추격 성공 메시지 반환
    return jsonify({"status": "success", "message": "추격 시각이 기록되었습니다."})

@app.route('/get_tracking_log')
def get_tracking_log():
    # 추격 시각 로그를 반환하는 함수
    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tracking_log ORDER BY timestamp DESC')
    logs = cursor.fetchall()
    conn.close()

    return jsonify(logs)

if __name__ == "__main__":
    init_db()  # 데이터베이스 및 테이블 초기화
    app.run(host="127.0.0.1", port=5000, threaded=True)
