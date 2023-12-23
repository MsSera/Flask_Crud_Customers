from flask import Flask, render_template, request, url_for, flash,jsonify,abort
from werkzeug.utils import redirect
from flask_jwt_extended import JWTManager, create_access_token
from flask_mysqldb import MySQL
import json
import dicttoxml

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'SECRET_KEY'  # Change this to a secure secret key
jwt = JWTManager(app)

# Your user authentication route
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')

    # Example: Check if the email exists in your database
    if email_exists_in_database(email):
        # If the email exists, create a JWT token
        access_token = create_access_token(identity=email)

        print(f"Generated token for {email}: {access_token}")

        return jsonify(access_token=access_token)
    else:
        return jsonify(error="Invalid credentials"), 401



# Replace this function with your actual check for email existence in the database
def email_exists_in_database(email):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute a query to check if a customer with the given email exists
    cur.execute("SELECT * FROM customers WHERE email_address = %s", (email,))
    customer_data = cur.fetchone()

    # Close the database connection
    cur.close()

    #print(f"Customer data for {email}: {customer_data}")

    # Check if a customer with the given email exists
    return customer_data is not None
# Load configuration from JSON file
with open('config.json') as config_file:
    config_data = json.load(config_file)

app.secret_key = config_data.get('SECRET_KEY', 'many random bytes')

app.config['MYSQL_HOST'] = config_data.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = config_data.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = config_data.get('MYSQL_PASSWORD', 'sera')
app.config['MYSQL_DB'] = config_data.get('MYSQL_DB', 'customer_jobs')
mysql = MySQL(app)

def get_output_format():
    # Get the format parameter from the query string, default to JSON
    return request.args.get('format', 'json').lower()

def convert_to_xml(data):
    # Convert dictionary to XML using dicttoxml library
    return dicttoxml.dicttoxml(data)
@app.route('/search', methods=['GET'])
def search():
    search_criteria = request.args.get('criteria')
    cur = mysql.connection.cursor()

    # Modify the query to search for names containing the specified criteria
    cur.execute("""
        SELECT * FROM customers 
        WHERE customer_first_name LIKE %s
    """, ('%' + search_criteria + '%',))

    data = cur.fetchall()
    cur.close()

    output_format = get_output_format()

    if output_format == 'xml':
        xml_data = convert_to_xml({'customers': data})
        return app.response_class(xml_data, content_type='application/xml')
    elif output_format == 'json':
        return jsonify(customers=data)
    else:
        return render_template('search_results.html', customers=data)

if __name__ == "__main__":
    app.run(debug=True)
