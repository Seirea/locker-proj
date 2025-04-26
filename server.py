import random
import duckdb
from flask import Flask, render_template, request, g

app = Flask(__name__)


def get_conn():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = duckdb.connect("locker.duckdb")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
@app.route("/index")
def front_page():
    return render_template("index.html")

@app.route("/lend")
def submit_page():
    return render_template("lend.html")

def code_gen(num_digits = 6):
    codeList = 0
    available_digits = [1,2,3,4,5,6,7,8,9,0]
    
    for i in range(num_digits):
        buffer = available_digits.pop(random.randrange(0,9))
        
        codeList += buffer
        if (i != num_digits-1):
            codeList *= 10

        available_digits.append(buffer)

    return codeList

@app.route("/69")
def meow():
    return int.to_bytes(code_gen(6), 4, "little", signed=False)

@app.post("/submit-item")
def submit_item():
    print(request.form)
    return "meow"

@app.get("/check-code")
def check_code():
    code = request.args.get("code", type=int)
    #location_id = request.args.get("location_id", type=int)
    
    cubby_id = request.args.get("cubby_id", type=int)
    res = get_conn().execute("SELECT code FROM Item WHERE item_id == $", [cubby_id]).fetchone()
    if res == None:
        raise RuntimeError("Could not find cubby");
    return res.trim() == code.trim()

@app.get("/search")
def search():
    query = request.args.get("query", type=str)
    res = conn.sql("")

    return str(res)

