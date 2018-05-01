from flask import *
import sys
import sqlite3
from functools import wraps
app = Flask(__name__)

DATABASE_FILE = "tables/database.db"
conn = sqlite3.connect(DATABASE_FILE)

def query_logger(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Executing query", *args, file=sys.stderr)
        try:
            return f(*args, **kwargs)
        except sqlite3.Error as e:
            print("SQL Error Occurred:", e.args[0], file=sys.stderr)
    return decorated_function

@query_logger
def execute(query):
    with conn:
        conn.executescript(query)

@query_logger
def fetchone(query):
    with conn:
        return conn.execute(query).fetchone()

@query_logger
def fetchall(query):
    with conn:
        return conn.execute(query).fetchall()

@app.route("/", methods=["GET, POST"])
def hello():
    if request.method == 'GET':
        query = "SELECT * FROM university;"
        entries = fetchall(query)

        return render_template("index.html", entries=entries)

    return render_template("index.html", entries = entries)

@app.route("/explore")
def explore():

    return render_template("search.html", entries=entries)

@app.route("/members/<string:name>/")
def getMember(name):
    return name


if __name__ == "__main__":
    app.run()