CREATE SEQUENCE location_id_seq START 1;

CREATE TABLE Location(
    location_id INTEGER PRIMARY KEY DEFAULT nextval('location_id_seq'),
    name VARCHAR,
    address VARCHAR
);

CREATE SEQUENCE user_id_seq START 1;

CREATE TABLE User(
    user_id INTEGER PRIMARY KEY DEFAULT nextval('user_id_seq'),
    name VARCHAR,
    phone_number INTEGER
);

CREATE SEQUENCE item_id_seq START 1;

CREATE TABLE Item (
    item_id INTEGER PRIMARY KEY DEFAULT nextval('item_id_seq'),
    item_name VARCHAR,
    owner_id INTEGER,
    description VARCHAR,
    image VARBINARY,
    image_ext VARCHAR,
    FOREIGN KEY (owner_id) REFERENCES User (user_id),
);

CREATE SEQUENCE cubby_id_seq START 1;

CREATE TABLE Cubby (
    cubby_id INTEGER PRIMARY KEY DEFAULT nextval('cubby_id_seq'),
    location_id INTEGER,
    item_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES Location (location_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id),
);