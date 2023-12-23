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
@app.route('/')
def Index_customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customers")
    data = cur.fetchall()
    cur.close()

    output_format = get_output_format()

    if output_format == 'xml':
        xml_data = convert_to_xml({'customers': data})
        return app.response_class(xml_data, content_type='application/xml')
    elif output_format == 'json':
        return jsonify(customers=data)
    else:
        # Render HTML template
        return render_template('index.html', customers=data)

@app.route('/insert_customers', methods = ['POST'])
def insert_customers():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        customer_id = request.form['customer_id']
        customer_first_name = request.form['customer_first_name']
        customer_middle_initial = request.form['customer_middle_initial']
        customer_last_name = request.form['customer_last_name']
        email_address = request.form['email_address']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        address = request.form['address']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO customers (customer_id,customer_first_name,customer_middle_initial,customer_last_name, gender, email_address, phone_number,address) VALUES (%s , %s , %s , %s , %s , %s, %s, %s)", (customer_id,customer_first_name,customer_middle_initial,customer_last_name,gender, email_address, phone_number,address))
        mysql.connection.commit()
        return redirect(url_for('Index_customers'))

@app.route('/delete_customers/<string:customer_id>', methods = ['GET'])
def delete_customers(customer_id):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))
    mysql.connection.commit()
    return redirect(url_for('Index_customers'))

@app.route('/update_customers', methods= ['POST', 'GET'])
def update_customers():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        customer_first_name = request.form['customer_first_name']
        customer_middle_initial = request.form['customer_middle_initial']
        customer_last_name = request.form['customer_last_name']
        email_address = request.form['email_address']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        address = request.form['address']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE customers SET customer_first_name=%s,customer_middle_initial=%s,customer_last_name=%s,gender=%s, email_address=%s, phone_number=%s, address=%s
        WHERE  customer_id=%s
        """, (customer_first_name,customer_middle_initial,customer_last_name,gender, email_address, phone_number,address, customer_id))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index_customers'))

@app.route('/index_jobs')
def Index_jobs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM jobs")
    data = cur.fetchall()
    cur.close()

    output_format = get_output_format()

    if output_format == 'xml':
        xml_data = convert_to_xml({'jobs': data})
        return app.response_class(xml_data, content_type='application/xml')
    elif output_format == 'json':
        return jsonify(jobs=data)
    else:
        # Render HTML template
        return render_template('index.html', jobs=data)

@app.route('/insert_jobs', methods=['POST'])
def insert_jobs():
    if request.method == "POST":
        try:
            flash("Data Inserted Successfully")
            job_id = request.form['job_id']
            customer_id = request.form['customer_id']
            date_job_started = request.form['date_job_started']
            date_job_completed = request.form['date_job_completed']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO jobs (job_id,customer_id,date_job_started,date_job_completed) VALUES (%s, %s, %s, %s)", (job_id, customer_id, date_job_started, date_job_completed))
            mysql.connection.commit()
            return redirect(url_for('Index_jobs'))
        except Exception as e:
            print(f"Error inserting data: {e}")
            return abort(400)


@app.route('/delete_jobs/<string:job_id>', methods = ['GET'])
def delete_jobs(job_id):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM jobs WHERE job_id=%s", (job_id,))
    mysql.connection.commit()
    return redirect(url_for('Index_jobs'))

from datetime import datetime
from flask import flash

@app.route('/update_jobs', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        job_id = request.form['job_id']
        customer_id = request.form['customer_id']
        date_job_started = request.form['date_job_started']
        date_job_completed = request.form['date_job_completed']

        # Convert date strings to datetime objects
        date_job_started = datetime.strptime(date_job_started, '%Y-%m-%d').date()
        date_job_completed = datetime.strptime(date_job_completed, '%Y-%m-%d').date()

        # Format dates as strings in the format 'YYYY-MM-DD'
        formatted_date_job_started = date_job_started.strftime('%Y-%m-%d')
        formatted_date_job_completed = date_job_completed.strftime('%Y-%m-%d')

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE jobs SET customer_id=%s, date_job_started=%s, date_job_completed=%s
            WHERE job_id=%s
            """, (customer_id, formatted_date_job_started, formatted_date_job_completed, job_id))

            flash("Data Updated Successfully")
            mysql.connection.commit()
            return redirect(url_for('Index_jobs'))
        except Exception as e:
            # Print or log the exception for debugging
            print("Error:", str(e))
            flash("Error updating data: {}".format(str(e)))

    return redirect(url_for('Index_jobs'))

@app.route('/index_standard')
def Index_standardt():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM standard_tasks")
    data = cur.fetchall()
    cur.close()

    output_format = get_output_format()

    if output_format == 'xml':
        xml_data = convert_to_xml({'standard_tasks': data})
        return app.response_class(xml_data, content_type='application/xml')
    elif output_format == 'json':
        return jsonify(standard_tasks=data)
    else:
        # Render HTML template
        return render_template('index.html', standard_tasks=data)

@app.route('/insert_standard', methods=['POST'])
def insert_standard():
    if request.method == "POST":
        try:
            flash("Data Inserted Successfully")
            task_id = request.form['task_id']
            task_name = request.form['task_name']
            task_price = request.form['task_price']
            task_description = request.form['task_description']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO standard_tasks (task_id,task_name,task_price,task_description) VALUES (%s, %s, %s, %s)", (task_id, task_name, task_price, task_description))
            mysql.connection.commit()
            return redirect(url_for('Index_standardt'))
        except Exception as e:
            print(f"Error inserting data: {e}")
            return abort(400)

@app.route('/delete_standard/<string:task_id>', methods = ['GET'])
def delete_standard(task_id):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM standard_tasks WHERE task_id=%s", (task_id,))
    mysql.connection.commit()
    return redirect(url_for('Index_standardt'))

@app.route('/update_standard', methods= ['POST', 'GET'])
def update_standard():
    if request.method == 'POST':
        task_id = request.form['task_id']
        task_name = request.form['task_name']
        task_price = request.form['task_price']
        task_description = request.form['task_description']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE standard_tasks SET task_name=%s,task_price=%s,task_description=%s
        WHERE  task_id=%s
        """, (task_name,task_price,task_description,task_id))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index_standardt'))



if __name__ == "__main__":
    app.run(debug=True)
