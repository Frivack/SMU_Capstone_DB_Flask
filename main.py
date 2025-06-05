import hashlib

from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': '127.0.0.1',
    'user': 'smu',
    'password': 'pV8qZr@31LwDbf$eTgXo',
    'database': 'pc_P'
}

# 기본 페이지
@app.route('/', methods=['GET'])
def index():
    return 'Server is running!', 200

# ---------------- 회원가입 ----------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    phone = data['phone']
    password = data['password']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, email, phone)
            VALUES (%s, %s, %s, %s)
        """, (username, password, email, phone))
        conn.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ---------------- 로그인 ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM users
            WHERE email = %s AND password= %s
        """, (email, password))
        user = cursor.fetchone()
        if user:
            return jsonify({'message': 'Login successful', 'user': user}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ---------------- 리뷰 조회 ----------------
@app.route('/reviews', methods=['GET'])
def get_reviews():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reviews")
        reviews = cursor.fetchall()
        return jsonify(reviews)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ---------------- 리뷰 작성 ----------------
@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.json
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reviews (user_id, title, content, created_at) VALUES (%s, %s, %s, NOW())",
            (data['userId'], data['title'], data['content'])
        )
        conn.commit()
        return jsonify({'message': 'Review added'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ---------------- 부품 전체 조회 ----------------
@app.route('/all-parts', methods=['GET'])
def get_all_parts():
    tables = [
        "cooler", "cpu", "earphone", "fan", "gpu", "hard_drive", "headset", "keyboard",
        "monitor", "motherboard", "mouse", "pc_case", "power_supply",
        "ram", "sound_card", "speaker"
    ]
    result = {}

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            result[table] = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
