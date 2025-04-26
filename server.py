import random
import duckdb
from flask import Flask, render_template
from flask import request

app = Flask(__name__)

conn = duckdb.connect("locker.duckdb")

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
    location_id = request.args.get("location_id", type=int)
    cubby_code = request.args.get("cubby_code", type=int)
    
    return "true"

@app.get("/search")
def search():
    query = request.args.get("query", type=str)
    res = conn.sql("")

    return str(res)

