from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

# MySQL database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Add your MySQL password here
    'database': 'bluechip'
}

# Function to connect to the MySQL database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# API to add a document verification stage for a student (POST method)
@app.route('/add_verification_stage', methods=['POST'])
def add_verification_stage():
    data = request.json
    student_id = data.get('student_id')
    stage = data.get('stage')
    status = data.get('status')

    if not student_id or not stage or not status:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO document_verification (student_id, stage, status)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (student_id, stage, status))
        conn.commit()

        return jsonify({'message': 'Verification stage added successfully!'}), 201

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()


# API to update a document verification stage (PUT method)
@app.route('/update_verification_stage/<int:student_id>', methods=['PUT'])
def update_verification_stage(student_id):
    data = request.json
    stage = data.get('stage')
    status = data.get('status')

    if not stage or not status:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        update_query = """
        UPDATE document_verification
        SET status = %s
        WHERE student_id = %s AND stage = %s
        """
        cursor.execute(update_query, (status, student_id, stage))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'No verification stage found for the given student ID'}), 404

        return jsonify({'message': 'Verification stage updated successfully!'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()


# API to fetch all verification stages for a student (GET method)
@app.route('/get_verification_stages/<int:student_id>', methods=['GET'])
def get_verification_stages(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM document_verification WHERE student_id = %s", (student_id,))
        verification_stages = cursor.fetchall()

        if verification_stages:
            return jsonify(verification_stages), 200
        else:
            return jsonify({'error': 'No verification stages found for the given student ID'}), 404

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
