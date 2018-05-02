from flask import *
import sys
import sqlite3
from functools import wraps
app = Flask(__name__)

DATABASE_FILE = "tables/database.db"
conn = sqlite3.connect(DATABASE_FILE)

university_columns = ["Name", "Region_ID", "City", "Student_Population", "Safety_Score", "Size"]
employment_columns = ["Name", "Percent_Employed", "Median_Earnings"]
cost_columns = ["Name", "Tuition_Cost", "Boarding_Cost", "Book_Cost"]
admissions_columns = ["Name", "Acceptance_Rate", "Average_SAT_Score", "Yield_Rate"]
location_columns = ["Name", "Region_ID", "Region_Name", "City", "State", "Fall_Weather", "Spring_Weather"]

all_college_columns = ["Name", "City", "State", "Student_Population", "Safety_Score", 
"Size", "Region_Name", "Fall_Weather", "Spring_Weather", "Percent_Employed", "Median_Earnings",
"Tuition_Cost", "Boarding_Cost", "Book_Cost", "Acceptance_Rate", "Average_SAT_Score", "Yield_Rate"]

col_aliases = ["u.Name", "u.City", "u.Student_Population", "u.Safety_Score", 
"u.Size", "l.State","l.Region_Name", "l.Fall_Weather", "l.Spring_Weather", "e.Percent_Employed", "e.Median_Earnings",
"c.Tuition_Cost", "c.Boarding_Cost", "c.Book_Cost", "a.Acceptance_Rate", "a.Average_SAT_Score", "a.Yield_Rate"]

table_aliases = {"university": "university as u", "employment": "employment as e", 
"admissions" : "admissions as a", "location":"location as l", "cost": "cost as c"}

joins_to_university = {"location": "u.University_ID = l.University_ID", "admissions": "u.University_ID = a.University_ID",
"cost": "u.University_ID = c.University_ID", "employment": "u.University_ID = e.University_ID"}

conn.row_factory = sqlite3.Row

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

@app.route("/", methods=["GET"])
def main_page():
    uni_rows = fetchall("SELECT Name FROM university ORDER BY Name ASC;")
    uni_list = [uni["Name"] for uni in uni_rows]

    city_rows = fetchall("SELECT DISTINCT City FROM university ORDER BY City ASC;")
    city_list = [city["City"] for city in city_rows]

    state_rows = fetchall("SELECT DISTINCT State FROM location ORDER BY State ASC;")
    state_list = [state["State"] for state in state_rows]

    region_rows = fetchall("SELECT DISTINCT Region_Name FROM location ORDER BY Region_Name ASC;")
    region_list = [region["Region_Name"] for region in region_rows]

    score_rows = fetchall("SELECT DISTINCT Safety_Score FROM university ORDER BY Safety_Score ASC; ")
    scores = [score["Safety_Score"] for score in score_rows]

    return render_template("index.html", uni_list = uni_list, city_list = city_list, 
        state_list= state_list, region_list=region_list, scores=scores)

@app.route("/results", methods = ["GET", "POST"])
def results():
    if request.method == "GET":
        return redirect(url_for('main_page'))

    selection_columns = ', '.join(col_aliases)
    query = ("SELECT " + selection_columns + " FROM university as u, admissions as a, cost as c, location as l, "
            "employment as e WHERE u.University_ID = a.University_ID AND u.University_ID = c.University_ID AND "
            "u.University_ID = l.University_ID AND u.University_ID = e.University_ID")
   
    form_fields = ["City", "State", "Student_Population", "Safety_Score", 
    "Size", "Region_Name", "Fall_Weather", "Spring_Weather", "Percent_Employed", "Median_Earnings",
    "Tuition_Cost", "Boarding_Cost", "Book_Cost", "Acceptance_Rate", "Average_SAT_Score"]
    
    conditions = []
    for item in form_fields:
        if request.form[item]:
            conditions.append(condition_lookup(item))

    if conditions:
        conditions = 'AND '.join(conditions)
        query = query + " AND " + conditions + ";"

    entries = fetchall(query)
    print(entries)
    if entries:
    	is_empty = False
    else:
    	is_empty = True

    return render_template("results.html", columns = all_college_columns, rows = entries, empty = is_empty)

@app.route('/university', methods = ["GET", "POST"])
def view_college():
    if request.method == "GET":
        return redirect(url_for('main_page'))

    college = request.form["university"]

    if college == "All Universities":
    	selection_columns = ', '.join(col_aliases)
    	query = ("SELECT " + selection_columns + " FROM university as u, admissions as a, cost as c, location as l, "
            "employment as e WHERE u.University_ID = a.University_ID AND u.University_ID = c.University_ID AND "
            "u.University_ID = l.University_ID AND u.University_ID = e.University_ID")
    	entries = fetchall(query)
    	print(entries)
    	if entries:
    		is_empty = False
    	else:
    		is_empty = True
    	return render_template("results.html", columns = all_college_columns, rows = entries, empty = is_empty)
    else:
    	selection_columns = ', '.join(col_aliases)
    	query = ("SELECT " + selection_columns + " FROM university as u, admissions as a, cost as c, location as l, "
        "employment as e WHERE u.University_ID = a.University_ID AND u.University_ID = c.University_ID AND "
        "u.University_ID = l.University_ID AND u.University_ID = e.University_ID AND u.Name ='{}';").format(college)

    	data = fetchone(query)
    	return render_template("college.html", university = college, columns = all_college_columns, row = data)

def build_query_plan():
    selection_columns = ', '.join(col_aliases)
    query = ("SELECT " + selection_columns + " FROM university as u, admissions as a, cost as c, location as l, "
            "employment as e WHERE u.University_ID = a.University_ID AND u.University_ID = c.University_ID AND "
            "u.University_ID = l.University_ID AND u.University_ID = e.University_ID")
   
    form_fields = ["City", "State", "Student_Population", "Safety_Score", 
    "Size", "Region_Name", "Fall_Weather", "Spring_Weather", "Percent_Employed", "Median_Earnings",
    "Tuition_Cost", "Boarding_Cost", "Book_Cost", "Acceptance_Rate", "Average_SAT_Score"]
    
    conditions = []
    print("Got Here")
    for item in form_fields:
        if request.form[item]:
            conditions.append(condition_lookup(item))

    print("Got Here")
    print(query)
    if not conditions:
        return query
    else:
        conditions = ' AND '.join(conditions)

    query = query + " AND " + conditions + ";"
    return query

def find_alias(item):
    if item in university_columns:
        return "u." + item
    elif item in employment_columns:
        return "e." + item
    elif item in cost_columns:
        return "c." + item
    elif item in admissions_columns:
        return "a." + item
    elif item in location_columns:
        return "l." + item
    else:
        raise Exception()

def condition_lookup(item):
    greater_than = ["Percent_Employed", "Median_Earnings", "Acceptance_Rate", "Spring_Weather", "Size"]
    less_than = ["Safety_Score", "Fall_Weather", "Student_Population", "Average_SAT_Score", "Tuition_Cost",
    "Boarding_Cost", "Book_Cost"]
    equal_to = ["Name", "City", "State", "Region_Name"]

    if item in greater_than:
        cond = find_alias(item) + " > " + convert(request.form[item])
    elif item in equal_to:
        cond = find_alias(item) + " = " + convert(request.form[item])
    elif item in less_than:
        cond = find_alias(item) + " < " + convert(request.form[item])
    else:
        raise Exception()

    return cond

def convert(item):
    if type(item) == str:
        return "'{}'".format(item)
    else:
    	return str(item) 

if __name__ == "__main__":
    app.run()