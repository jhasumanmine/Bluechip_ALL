from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# MySQL database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bluechip"
)

# 1. GET /api/stats
# Purpose: Retrieve total counts for students, agents, leads, and converted leads.
@app.route('/api/stats', methods=['GET'])
def get_stats():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM students) AS total_students,
            (SELECT COUNT(*) FROM agents) AS total_agents,
            (SELECT COUNT(*) FROM leads) AS total_leads,
            (SELECT COUNT(*) FROM converted_leads) AS total_converted_leads
    """)
    stats = cursor.fetchone()
    return jsonify(stats), 200


# 2. GET /api/students/bluechip
# Purpose: Retrieve a list of students registered directly through Bluechip.
@app.route('/api/students/bluechip', methods=['GET'])
def get_bluechip_students():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT student_id, name, email, phone
        FROM students
        WHERE registered_via = 'bluechip';
    """)
    students = cursor.fetchall()
    return jsonify(students), 200


# 3. GET /api/students/agents
# Purpose: Retrieve a list of students registered through agents.
@app.route('/api/students/agents', methods=['GET'])
def get_agent_students():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.student_id, s.name, s.email, s.phone, a.agent_name
        FROM students s
        JOIN leads l ON s.student_id = l.student_id
        JOIN agents a ON l.agent_id = a.agent_id
        WHERE s.registered_via = 'agent';
    """)
    students = cursor.fetchall()
    return jsonify(students), 200


# 4. GET /api/students/<int:id>
# Purpose: Retrieve full details of a student by student_id, including the agent they were registered through.
@app.route('/api/students/<int:id>', methods=['GET'])
def get_student_by_id(id):
    cursor = db.cursor(dictionary=True)
    
    # Updated SQL query to include agent name or 'bluechip' if no agent
    cursor.execute("""
        SELECT s.student_id, s.name, s.email, s.phone, s.registration_date, s.is_converted, s.registered_via,
               COALESCE(a.agent_name, 'bluechip') AS agent_name
        FROM students s
        LEFT JOIN leads l ON s.student_id = l.student_id
        LEFT JOIN agents a ON l.agent_id = a.agent_id
        WHERE s.student_id = %s
    """, (id,))
    
    student = cursor.fetchone()
    if student:
        return jsonify(student), 200
    else:
        return jsonify({"error": "Student not found"}), 404


# 5. GET /api/leads
# Purpose: Retrieve a list of all leads.
@app.route('/api/leads', methods=['GET'])
def get_all_leads():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.lead_id, s.name AS student_name, a.agent_name, l.status
        FROM leads l
        JOIN students s ON l.student_id = s.student_id
        LEFT JOIN agents a ON l.agent_id = a.agent_id
    """)
    leads = cursor.fetchall()
    return jsonify(leads), 200


# 6. POST /api/leads
# Purpose: Create a new lead entry.
# @app.route('/api/leads', methods=['POST'])
# def create_lead():
#     data = request.json
#     student_id = data['student_id']
#     agent_id = data.get('agent_id')  # Optional field, may be null
#     status = data.get('status', 'pending')

#     cursor = db.cursor()

#     # Insert a new lead
#     cursor.execute("""
#         INSERT INTO leads (student_id, agent_id, status)
#         VALUES (%s, %s, %s)
#     """, (student_id, agent_id, status))

#     db.commit()
#     return jsonify({"message": "Lead created successfully"}), 201


# 7. GET /api/converted-leads
# Purpose: Retrieve a list of all converted leads with conversion dates.
@app.route('/api/converted-leads', methods=['GET'])
def get_converted_leads():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT cl.converted_lead_id, l.lead_id, s.name AS student_name, cl.conversion_date
        FROM converted_leads cl
        JOIN leads l ON cl.lead_id = l.lead_id
        JOIN students s ON l.student_id = s.student_id
    """)
    converted_leads = cursor.fetchall()
    return jsonify(converted_leads), 200


# 8. POST /api/converted-leads
# Purpose: Convert a lead into a converted lead.
@app.route('/api/converted-leads', methods=['POST'])
def convert_lead():
    data = request.json
    lead_id = data['lead_id']
    conversion_date = datetime.now()  # Automatically set to current date and time

    cursor = db.cursor()

    # Insert into converted leads
    cursor.execute("""
        INSERT INTO converted_leads (lead_id, conversion_date)
        VALUES (%s, %s)
    """, (lead_id, conversion_date))

    # Update the lead status to 'converted'
    cursor.execute("""
        UPDATE leads
        SET status = 'converted'
        WHERE lead_id = %s
    """, (lead_id,))

    db.commit()
    return jsonify({"message": "Lead converted successfully"}), 201



#For student details section goto StudentDash file and find the endpoint there and integrate it
# Run the Flask app

if __name__ == '__main__':
    app.run(debug=True)
