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

CREATE TABLE Item (
    item_id INTEGER PRIMARY KEY,
    item_name VARCHAR,
    owner_id INTEGER,
    description VARCHAR,
    image VARBINARY,
    FOREIGN KEY (owner_id) REFERENCES User (user_id),
);

CREATE TABLE Cubby (
    cubby_id INTEGER PRIMARY KEY,
    location_id INTEGER,
    item_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES Location (location_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id),
);