from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': '127.0.0.1',
    'user': 'smu',
    'password': 'pV8qZr@31LwDbf$eTgXo',
    'database': 'pc_P'
}

# 허용할 테이블 목록
allowed_tables = ['reviews', 'users']

# 기본 페이지
@app.route('/', methods=['GET'])
def index():
    return 'Server is running!', 200

@app.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200

# 테이블 데이터 조회
@app.route('/get-data/<table_name>', methods=['GET'])
def get_data_route(table_name):
    if table_name not in allowed_tables:
        return jsonify({'error': 'Invalid table name'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
