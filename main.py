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
            SELECT id AS user_id, email FROM users
            WHERE email = %s AND password = %s
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
    # URL 쿼리 파라미터에서 값 가져오기 (예: /all-parts?theme=1&limit=10&offset=0)
    theme_id = request.args.get('theme', type=int)
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)

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
            # 기본 SQL 쿼리
            query = f"SELECT * FROM {table}"
            params = []

            # 테마 ID에 따라 WHERE 절 추가
            where_clauses = []
            if theme_id is not None:
                if theme_id == 1:  # 1: 블랙 & 화이트
                    where_clauses.append("color IN ('Black', 'White')")
                elif theme_id == 2:  # 2: RGB
                    where_clauses.append("name LIKE %s")
                    params.append('%RGB%')
                elif theme_id == 3:  # 3: 블랙
                    where_clauses.append("color = %s")
                    params.append('Black')
                elif theme_id == 4:  # 4: 화이트
                    where_clauses.append("color = %s")
                    params.append('White')
                elif theme_id == 5:  # 5: 핑크 & 퍼플
                    where_clauses.append("color IN ('Pink', 'Purple')")

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            # 페이지네이션을 위한 LIMIT, OFFSET 추가
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, tuple(params))
            result[table] = cursor.fetchall()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
