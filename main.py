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

    theme_applicable_tables = [
        "cooler", "earphone", "fan", "headset", "keyboard", "monitor",
        "mouse", "pc_case", "ram", "speaker"
    ]

    result = {}

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        theme_masks = {
            # 블랙 & 화이트 (특별 처리)
            2: 4,  # RGB
            3: 16,  # 블랙
            4: 2,  # 화이트
            5: 8  # 핑크 & 퍼플
        }

        for table in tables:
            query = f"SELECT * FROM {table}"
            params = []

            if table in theme_applicable_tables and theme_id is not None:
                where_clauses = []
                # 블랙(16) 또는 화이트(2)
                if theme_id == 1:
                    where_clauses.append("(CAST(theme AS UNSIGNED) & %s > 0 OR CAST(theme AS UNSIGNED) & %s > 0)")
                    params.extend([16, 2])
                elif theme_id in theme_masks:
                    mask = theme_masks[theme_id]
                    where_clauses.append("CAST(theme AS UNSIGNED) & %s > 0")
                    params.append(mask)

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, tuple(params))
            table_result = cursor.fetchall()

            if not table_result and table in theme_applicable_tables and theme_id is not None:
                print(f"No results for table {table} with theme {theme_id}. Fetching default parts.")
                default_query = f"SELECT * FROM {table} LIMIT %s OFFSET %s"
                cursor.execute(default_query, (limit, offset))
                table_result = cursor.fetchall()

            result[table] = table_result

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
