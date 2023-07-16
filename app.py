import sqlite3
from flask import Flask, redirect, render_template, request, url_for
from flask.sessions import NullSession


app = Flask(__name__, static_folder='static')


# Additional app configuration and routes...

@app.route('/')
def welcome():
    return render_template('wel.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        country = request.form['country']
        accreate = request.form['accreate']
        
        # Check if the username already exists
        if check_existing_username(username):
            error_message = 'The username already exists.'
            return render_template('regi.html', error_message=error_message)
        
        # Store the credentials
        register_store_credentials(username, password, country, accreate)
        
        # Redirect to the login page
        return redirect(url_for('admin'))
    
    return render_template('regi.html', error_message='')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username and password are correct
        if check_credentials(username, password):    

            login_store_credentials(username, password)        
            # Redirect to the search page
            return redirect(url_for('search'))
        else:
            error_message = 'The username or password is wrong.'
            return render_template('admi.html', error_message=error_message)

    return render_template('admi.html', error_message='')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        return redirect(url_for('results', search_term=search_term))  # Use the endpoint name 'results'
    return render_template('search2.html')

# Route for results page
@app.route('/results')

def results():
    search_term = request.args.get('search_term', '')
    search_results = search_names(search_term)
    return render_template('results.html', results=search_results)

import sqlite3

def register_store_credentials(username, password, country, accreate):
    conn = sqlite3.connect('ten.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, country TEXT, accreate TEXT)")
    cursor.execute("INSERT INTO users (username, password, country, accreate) VALUES (?, ?, ?, ?)", (username, password, country, accreate))
    cursor.execute("CREATE TABLE IF NOT EXISTS alusers (username TEXT PRIMARY KEY, password TEXT)")
    cursor.execute("INSERT INTO alusers (username, password) VALUES (?, ?)", (username, password))
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS insert_alusers_trigger
        AFTER INSERT ON users
        BEGIN
            INSERT INTO alusers (username, password)
            VALUES (NEW.username, NEW.password);
        END;
    """)
    conn.commit()
    conn.close()

def login_store_credentials(username, password):
    conn = sqlite3.connect('ten.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS alusers (username TEXT PRIMARY KEY, password TEXT)")
    cursor.execute("INSERT INTO alusers (username, password) SELECT username, password FROM users WHERE username = ? AND password = ?", (username, password))
    conn.commit()
    conn.close()


   


def check_existing_username(username):
    conn = sqlite3.connect('ten.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM alusers WHERE username = ?", (username,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def check_credentials(username, password):
    conn = sqlite3.connect('ten.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM alusers WHERE username = ? AND password = ?", (username, password))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def search_names(search_term):
    conn = sqlite3.connect('ten.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM names WHERE name LIKE ?", ('%' + search_term + '%',))
    search_results = cursor.fetchall()
    conn.close()
    return search_results

def details(search_term):
    conn = sqlite3.connect('ten.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT de.id, de.name, de.location, de.items, de.lat_long, de.full_details
        FROM de
        JOIN names ON de.name = names.name
        WHERE name LIKE ?
    """, ('%' + search_term + '%',))
    search_results = cursor.fetchall()
    conn.close()
    return search_results

if __name__ == '__main__':
    app.debug = True
    app.run()
