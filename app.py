from flask import Flask, request, render_template
import sqlite3
import os

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Create data table with foreign key to results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode INTEGER NOT NULL,
            reward_min REAL NOT NULL,
            reward_mean REAL NOT NULL,
            reward_max REAL NOT NULL,
            episode_length INTEGER NOT NULL,
            result_id INTEGER NOT NULL,
            FOREIGN KEY (result_id) REFERENCES results (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Route to handle data submission
@app.route('/submit', methods=['POST'])
def submit_data():
    episode = request.form['episode']
    reward_min = request.form['reward_min']
    reward_mean = request.form['reward_mean']
    reward_max = request.form['reward_max']
    episode_length = request.form['episode_length']
    timestamp = request.form['timestamp']
    checkpoint = request.form['checkpoint']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Insert into results table
    cursor.execute('INSERT INTO results (timestamp) VALUES (?)', (timestamp,))
    result_id = cursor.lastrowid
    
    # Insert into data table
    cursor.execute('''
        INSERT INTO data (episode, reward_min, reward_mean, reward_max, episode_length, result_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (episode, reward_min, reward_mean, reward_max, episode_length, result_id))
    
    conn.commit()
    conn.close()
    return 'Data submitted successfully!\n'

# Route to display list of results
@app.route('/results')
def list_results():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM results')
    results = cursor.fetchall()
    conn.close()
    return render_template('results.html', results=results)

# Route to display data for a specific result
@app.route('/results/<int:result_id>')
def list_data(result_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.id, d.episode, d.reward_min, d.reward_mean, d.reward_max, d.episode_length, r.timestamp
        FROM data d
        JOIN results r ON d.result_id = r.id
        WHERE d.result_id = ?
    ''', (result_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('data.html', data=data)

if __name__ == '__main__':
    init_db()
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=True)