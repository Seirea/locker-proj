CREATE TABLE Location(
    location_id INTEGER PRIMARY KEY,
    name VARCHAR,
    address VARCHAR
);

CREATE TABLE User(
    user_id INTEGER PRIMARY KEY,
    name VARCHAR,
    phone_number INTEGER
);

CREATE TABLE Item(
    item_id INTEGER PRIMARY KEY,
    location_id INTEGER,
    name VARCHAR,
    description VARCHAR,
    image VARBINARY,
    owner_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES Location (location_id),
    FOREIGN KEY (owner_id) REFERENCES User (user_id),
);