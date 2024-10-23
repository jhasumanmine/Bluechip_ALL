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

# Main folder for document uploads
MAIN_UPLOAD_FOLDER = 'uploaded_documents'
os.makedirs(MAIN_UPLOAD_FOLDER, exist_ok=True)  # Ensure the main folder exists
app.config['MAIN_UPLOAD_FOLDER'] = MAIN_UPLOAD_FOLDER

# Function to connect to the MySQL database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# API to allow students to upload documents (POST method)
@app.route('/upload_documents', methods=['POST'])
def upload_documents():
    documents = ['resume', 'passport_copy', 'marksheet_10', 'marksheet_12', 'degree_transcript',
                 'diploma_pgdm', 'pdc', 'lor', 'experience_letter', 'sop']
    
    file_paths = {}

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert initial entry to generate a new student_id
        insert_initial_query = """
        INSERT INTO student_document (resume, passport_copy, marksheet_10, marksheet_12, 
                                      degree_transcript, diploma_pgdm, pdc, lor, 
                                      experience_letter, sop)
        VALUES (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
        """
        cursor.execute(insert_initial_query)
        conn.commit()

        # Get the newly generated student_id
        student_id = cursor.lastrowid

        # Create a folder for the student based on student_id
        student_folder = os.path.join(app.config['MAIN_UPLOAD_FOLDER'], f"student_{student_id}")
        os.makedirs(student_folder, exist_ok=True)  # Create the student's folder

        # Loop through all document fields and save uploaded files in the student's folder
        for doc in documents:
            file = request.files.get(doc)
            if file:
                file_path = os.path.join(student_folder, file.filename)
                file.save(file_path)  # Save the file to the student's folder
                file_paths[doc] = file_path  # Store file path for database insertion

        # Update the student_document table with the file paths
        update_query = """
        UPDATE student_document
        SET resume = %s, passport_copy = %s, marksheet_10 = %s, marksheet_12 = %s, 
            degree_transcript = %s, diploma_pgdm = %s, pdc = %s, lor = %s, 
            experience_letter = %s, sop = %s
        WHERE student_id = %s
        """
        cursor.execute(update_query, (
            file_paths.get('resume'),
            file_paths.get('passport_copy'),
            file_paths.get('marksheet_10'),
            file_paths.get('marksheet_12'),
            file_paths.get('degree_transcript'),
            file_paths.get('diploma_pgdm'),
            file_paths.get('pdc'),
            file_paths.get('lor'),
            file_paths.get('experience_letter'),
            file_paths.get('sop'),
            student_id
        ))
        conn.commit()

        return jsonify({'message': 'Documents uploaded successfully!', 'student_id': student_id}), 201

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()


#This API will be fetched at admin dashboard to view the student documents
#Kinfdly integrate this api in admin dashboard "student detail" section.


# API for admin to fetch student documents by student ID (GET method)
@app.route('/get_student_documents/<int:student_id>', methods=['GET'])
def get_student_documents(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch the student documents based on student ID
        cursor.execute("SELECT * FROM student_document WHERE student_id = %s", (student_id,))
        student_documents = cursor.fetchone()

        if student_documents:
            return jsonify(student_documents), 200
        else:
            return jsonify({'error': 'No documents found for the given student ID'}), 404

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()


# API to add additional information for a student (POST method)
@app.route('/add_additional_info', methods=['POST'])
def add_additional_info():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Extract data from request
        data = request.json
        student_id = data['student_id']
        preferred_university = data.get('preferred_university')
        preferred_country = data.get('preferred_country')
        preferred_intake = data.get('preferred_intake')
        budget = data.get('budget')
        phone = data.get('phone')
        dob = data.get('dob')
        special_request = data.get('special_request')

        # Insert query to add additional information
        insert_query = """
        INSERT INTO student_additional_info (student_id, preferred_university, preferred_country, preferred_intake, budget, phone, dob, special_request)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            student_id, 
            preferred_university, 
            preferred_country, 
            preferred_intake, 
            budget, 
            phone, 
            dob, 
            special_request
        ))
        conn.commit()

        return jsonify({'message': 'Additional information added successfully!'}), 201

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()


# API to fetch additional information of a student by student ID (GET method)
@app.route('/get_additional_info/<int:student_id>', methods=['GET'])
def get_additional_info(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch the additional information based on student ID
        cursor.execute("SELECT * FROM student_additional_info WHERE student_id = %s", (student_id,))
        additional_info = cursor.fetchone()

        if additional_info:
            return jsonify(additional_info), 200
        else:
            return jsonify({'error': 'No additional information found for the given student ID'}), 404

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
