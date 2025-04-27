import random
import threading
import duckdb
import nltk
from pathlib import Path
from duckdb.typing import VARCHAR, INTEGER
from flask import Flask, render_template, request, g, send_file, Response
from werkzeug.exceptions import RequestEntityTooLarge

# Initialize Flask Application
app = Flask(__name__)

# Set max file upload size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

DB_CONN = None

# Lazy DB Connection
def get_conn():
    global DB_CONN
    db = DB_CONN
    # If connection is not established currently, create a connection!
    if (db is None):
        print("Creating DB CONNECTION")
        # Check if file exists, in order to add DB Tables
        exists = Path("./locker.duckdb").exists()
        # Create connection
        DB_CONN = duckdb.connect("locker.duckdb")
        db = DB_CONN
        # Add string distance, for searching
        # try:
        #     db.remove_function("dist")
        # except:
        #     pass
        db.create_function("dist", dist)
        # Run DB Schema from SQueaL file
        if not exists:
            with open("./db.sql", "r") as f:
                db.sql(f.read())
        return db

    return db

# close connection whenever application closes
# @app.teardown_appcontext
# def close_connection(exception):
#     print("CLOSING CONNECTION")
#     db = DB_CONN
#     if not (db is None): # only if connection exists
#         db.close()

# Basic error screen for the runtime errors
@app.errorhandler(RuntimeError)
def handle_bad_request(e):
    return f"""
    <h1>An error occured with the server</h1>
    <code>{e}</code>
    <br />
    <a href="/">Go back to homepage</a>
    """, 500

# Max file size error
@app.errorhandler(RequestEntityTooLarge)
def handle_too_big(e):
    return f"""
    <h1>The file uploaded was too big! Max 16 MB</h1>
    <br />
    <a href="/">Go back to homepage</a>
    """, 413


# render borrowing page
@app.route("/")
@app.route("/index")
def front_page():
    return render_template("index.html")

# render lending page
@app.route("/lend")
def submit_page():
    return render_template("lend.html")

# establishes admin console accessible through `$ deno run --allow-net sql_client.js`
@app.route("/admin-execute-sql", methods=["POST"])
def get_locations():
    cmd = request.data.decode()
    print("EXECUTING:", cmd)
    res = get_conn().sql(cmd)
    return str(res)

# Generate combination code for unlocking
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

# Checks if uploaded image IS an image
ALLOWED_EXTENSIONS=["png", "jpg", "jpeg", "jxl", "gif", "webp", "avif", "heif"]
def get_fext(filename):
    return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return '.' in filename and get_fext(filename) in ALLOWED_EXTENSIONS


# Form action for submitting a lend
@app.post("/lend-item")
def lend_item():
    loc = request.values.get("location", type=int) or 1
    item_name = request.values.get("item-name", type=str)
    item_description = request.values.get("item-description", type=str)
    if not item_name or not item_description:
        raise RuntimeError("Item name and description required!")
        
    image = request.files.get("image")

    #if image and allowed_file(image.filename):
    print(f"Creating item {item_name} for location {loc}")

    cubby_id = get_conn().execute("SELECT cubby_id FROM Cubby WHERE location_id == $1 AND item_id is NULL", [loc]).fetchone()
    if cubby_id is None:
        raise RuntimeError("Could not find a free cubby in this location");
    cubby_id = cubby_id[0]
    print(f"using cubby id: {cubby_id}")

    generated_item_id = get_conn().execute("INSERT INTO Item VALUES(DEFAULT, $1, $2, $3, $4) RETURNING (item_id)", [item_name, item_description, image.read(), get_fext(image.filename)]).fetchone()[0]
    print("generated item id:", generated_item_id)
    res = get_conn().execute("UPDATE cubby SET item_id = $1, code = $2 WHERE cubby_id == $3 RETURNING code, cubby_id", [generated_item_id, code_gen(), cubby_id]).fetchone()
    print("RETURNING:", res)

    return render_template("lend_response.html", cubby_id=res[1], cubby_code=res[0])

# Item image endpoint
@app.get("/item-image/<id>")
def item_img(id: int):
    # Get image from database
    res = get_conn().execute("SELECT image, image_ext FROM Item WHERE item_id == $1", [id]).fetchone();
    # If exists, send it back to the client
    if data := res:
        img, ext = data
        return Response(img, mimetype=f"image/{ext}")
    # Else send an error
    return f"""
    <h1>Image not found</h1>
    <br />
    <a href="/">Go back to homepage</a>
    """, 404

# borrow item
@app.get("/borrow/<id>")
def borrow_item(id: int):
    # Get image from database
    res = get_conn().execute("SELECT cubby_id, code, item_id FROM Cubby WHERE item_id == $1", [id]).fetchone();
    # If exists, send it back to the client
    if data := res:
        cubby_id, code, item_id = data
        get_conn().execute("UPDATE cubby SET item_id = NULL WHERE cubby_id == $1", [cubby_id]).fetchone()
        get_conn().execute("DELETE FROM item WHERE item_id == $1", [id]).fetchone()
        return render_template("lend_response.html", cubby_id=cubby_id, cubby_code=code)
    # Else send an error
    return f"""
    <h1>Image not found</h1>
    <br />
    <a href="/">Go back to homepage</a>
    """, 404

@app.get("/check-code")
def check_code():
    code = request.values.get("code", type=int)
    #location_id = request.values.get("location_id", type=int)
    cubby_id = request.values.get("cubby_id", type=int)

    real_code = get_conn().execute("SELECT code FROM Cubby WHERE cubby_id == $1", [cubby_id]).fetchone()
    if real_code is None:
        raise RuntimeError("Could not find cubby");

    # print(f"CHECK CODE REQUEST: {code}, {cubby_id}, ")

    return real_code == code

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
    

    return render_template("search_results.html", results=res)

if __name__ == "__main__":
    app.run(debug=True, threaded=True) # Ensure threading is enabled for testing