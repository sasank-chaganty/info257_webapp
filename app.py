from flask import Flask, render_template
app = Flask(__name__)
 
@app.route("/")
def index():
	entries = database.execute()
	render_template("index.html", entries=entries)
 
@app.route("/hello")
def hello():
    return "Hello World!"
 
@app.route("/members")
def members():
    return "Members"
 
@app.route("/members/<string:name>/")
def getMember(name):
    return name
 
if __name__ == "__main__":
    app.run()