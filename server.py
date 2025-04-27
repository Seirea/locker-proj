import random
import duckdb
from duckdb.typing import VARCHAR, INTEGER

from flask import Flask, render_template, request, g

app = Flask(__name__)


def get_conn():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = duckdb.connect("locker.duckdb")
        db.create_function("dist", dist)

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

@app.route("/admin-execute-sql", methods=["POST"])
def get_locations():
    cmd = request.data.decode()
    print("EXECUTING:", cmd)
    res = get_conn().sql(cmd)
    return str(res)

def code_gen(num_digits = 6):
    code_list = 0
    available_digits = [1,2,3,4,5,6,7,8,9,0]
    
    for i in range(num_digits):
        buffer = available_digits.pop(random.randrange(0,9))
        
        code_list += buffer
        if (i != num_digits-1):
            code_list *= 10

        available_digits.append(buffer)

    return code_list

@app.route("/69")
def meow():
    return int.to_bytes(code_gen(6), 4, "little", signed=False)

@app.post("/lend-item")
def lend_item():
    loc = request.args.get("location", type=int)

    res = get_conn().execute("SELECT cubby_id FROM Cubby WHERE location_id == $1 AND item_id == null", [loc]).fetchone()

    if (res == None):
        raise RuntimeError("Could not find a free cubby in this location");

    # get_conn().execute("")

    return str(res)

@app.get("/check-code")
def check_code():
    code = request.args.get("code", type=int)
    #location_id = request.args.get("location_id", type=int)

    cubby_id = request.args.get("cubby_id", type=int)
    res = get_conn().execute("SELECT code FROM Item WHERE item_id == $", [cubby_id]).fetchone()
    if res == None:
        raise RuntimeError("Could not find cubby");

    return res.trim() == code.trim()

end_flag = False

def tail(s1, s2):
    index = 0
    max_index = min(len(s1), len(s2))

    while(index < max_index and s1[index] == s2[index]):
        index += 1

    return s1[index:]

def lev_dist(s, target, stop_dist) -> int:
    if stop_dist == 0:
        return int("inf")

    if s == "" or target == "":
        end_flag = True
        return 0

    tail_s = tail(s, target)
    tail_t = tail(s, target)

    if tail_s == tail_t:
        return lev_dist(tail_s, tail_t, stop_dist-1)

    return 1 + min(lev_dist(s, tail_t, stop_dist-1),
                    lev_dist(tail_s, target, stop_dist-1),
                    lev_dist(tail_s, tail_t, stop_dist-1))

def dist(s: str, target: str) -> int:
    return lev_dist(s, target, max(len(s), len(target)) + 1)


@app.get("/search")
def searchLocations():
    query = request.args.get("query", type=str) or ""
    count = request.args.get("count", type=int) or 5
    print(query)
    res = get_conn().execute('SELECT name, address FROM Location ORDER BY dist(address, $1) LIMIT $2', [str(query), count]).fetchall()

    return str(res)