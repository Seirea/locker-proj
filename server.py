import random
import duckdb
from flask import Flask, render_template
from flask import request

app = Flask(__name__)

conn = duckdb.connect("locker.duckdb")

@app.route("/")
@app.route("/index")
def hello_world():
    return render_template("index.html")

def code_gen():
    codeList = 0
    digits = [i for i in range(10)]
    buffer = random.randrange(0,10)
    digits.remove(buffer)

    for i in range(7):
        codeList *= 10
        codeList += buffer

        digits.append(buffer)
        buffer = digits[random.randrange(0,9)]
        digits.remove(buffer)

    return codeList

@app.route("/69")
def meow():
    return str(code_gen())

@app.post("/submit-item")
def submit_item():
    print(request.form)
    return "meow"

@app.get("/check-code")
def check_code():
    code = request.args.get("code", type=int)
    location_id = request.args.get("location_id", type=int)
    cubby_code = request.args.get("cubby_code", type=int)
    
    return "true"

@app.get("/search")
def search():
    query = request.args.get("query", type=str)
    res = conn.sql("")

    return str(res)

