import random
import duckdb
import nltk
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
    loc = request.values.get("location", type=int)

    res = get_conn().execute("SELECT cubby_id FROM Cubby WHERE location_id == $1 AND item_id == null", [loc]).fetchone()

    if (res == None):
        raise RuntimeError("Could not find a free cubby in this location");

    # get_conn().execute("")

    return str(res)

@app.get("/check-code")
def check_code():
    code = request.values.get("code", type=int)
    #location_id = request.values.get("location_id", type=int)

    cubby_id = request.values.get("cubby_id", type=int)
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
    return nltk.edit_distance(s, target)
    # return lev_dist(s, target, max(len(s), len(target)) + 1)


@app.post("/search")
def search_handler():
    query_type = request.values.get("type", type=str) or "Location"
    query = request.values.get("query", type=str) or ""
    count = request.values.get("count", type=int) or 5
    match query_type:
        case "Location":
            return search_location(query, count);
        case "Item":
            return search_item(query, count);


def search_location(query, count):
    res = get_conn().execute('SELECT name, address FROM Location ORDER BY dist(name, $1) LIMIT $2', [str(query), count]).fetchall()

    return str(res)

def search_item(query, count):
    res = get_conn().execute('SELECT item_id, item_name FROM Item ORDER BY dist(item_name, $1) LIMIT $2', [str(query), count]).fetchall()

    return str(res)