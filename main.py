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
        theme_masks = {
            1: 16,  # 블랙 & 화이트 (특별 처리 필요)
            2: 4,  # RGB
            3: 16,  # 블랙
            4: 2,  # 화이트
            5: 8  # 핑크 & 퍼플
        }

        for table in tables:
            query = f"SELECT * FROM {table}"
            params = []
            where_clauses = []

            cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'theme'")
            has_theme_column = cursor.fetchone() is not None

            if has_theme_column and theme_id is not None:
                if theme_id == 1:
                    where_clauses.append("(CAST(theme AS UNSIGNED) & %s > 0 OR CAST(theme AS UNSIGNED) & %s > 0)")
                    params.extend([theme_masks[3], theme_masks[4]])

                elif theme_id in theme_masks:
                    mask = theme_masks[theme_id]
                    # 비트 연산 쿼리️
                    where_clauses.append("CAST(theme AS UNSIGNED) & %s > 0")
                    params.append(mask)

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
