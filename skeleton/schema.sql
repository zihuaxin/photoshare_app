CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS Friends;
DROP TABLE IF EXISTS Likes;
DROP TABLE IF EXISTS Comments;
DROP TABLE IF EXISTS Tagged;
DROP TABLE IF EXISTS Photos;
DROP TABLE IF EXISTS Tags;
DROP TABLE IF EXISTS Albums;
DROP TABLE IF EXISTS Users;


CREATE TABLE Users(
 user_id INTEGER AUTO_INCREMENT,
 first_name VARCHAR(100),
 last_name VARCHAR(100),
 email VARCHAR(100),
 birth_date DATE,
 hometown VARCHAR(100),
 gender VARCHAR(100),
 password VARCHAR(100) NOT NULL,
 PRIMARY KEY (user_id),
 UNIQUE (email)
 );

 CREATE TABLE Friends(
 user_id1 INTEGER,
 user_id2 INTEGER,
 PRIMARY KEY (user_id1, user_id2),
 FOREIGN KEY (user_id1)
 REFERENCES Users(user_id),
 FOREIGN KEY (user_id2)
 REFERENCES Users(user_id)
);

CREATE TABLE Albums(
 albums_id INTEGER AUTO_INCREMENT,
 name VARCHAR(100),
 date DATE,
 user_id INTEGER NOT NULL,
 PRIMARY KEY (albums_id),
 FOREIGN KEY (user_id)
 REFERENCES Users(user_id)
);

CREATE TABLE Tags(
 tag_id INTEGER AUTO_INCREMENT,
 name VARCHAR(100),
 PRIMARY KEY (tag_id)
);

CREATE TABLE Photos(
 photo_id INTEGER AUTO_INCREMENT,
 caption VARCHAR(100),
 data LONGBLOB,
 albums_id INTEGER NOT NULL,
 user_id INTEGER NOT NULL,
 PRIMARY KEY (photo_id),
 FOREIGN KEY (albums_id) REFERENCES Albums (albums_id),
 FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

CREATE TABLE Tagged(
 photo_id INTEGER,
 tag_id INTEGER,
 PRIMARY KEY (photo_id, tag_id),
 FOREIGN KEY(photo_id)
 REFERENCES Photos (photo_id),
 FOREIGN KEY(tag_id)
 REFERENCES Tags (tag_id)
);

CREATE TABLE Comments(
 comment_id INTEGER AUTO_INCREMENT,
 user_id INTEGER NOT NULL,
 photo_id INTEGER NOT NULL,
 text VARCHAR (100),
 date DATE,
 PRIMARY KEY (comment_id),
 FOREIGN KEY (user_id)
 REFERENCES Users (user_id),
 FOREIGN KEY (photo_id)
 REFERENCES Photos (photo_id)
);

CREATE TABLE Likes(
 photo_id INTEGER,
 user_id INTEGER,
 PRIMARY KEY (photo_id,user_id),
 FOREIGN KEY (photo_id)
 REFERENCES Photos (photo_id),
 FOREIGN KEY (user_id)
 REFERENCES Users (user_id),
 UNIQUE (photo_id, user_id)
);

INSERT INTO Users(user_id, first_name, last_name, email, birth_date, hometown, gender, password)
VALUES (1, "Jasper", "Xin", "zihuaxin@bu.edu", CURRENT_DATE(), "China", "male", "test");

INSERT INTO Users(first_name, last_name, email, birth_date, hometown, gender, password)
VALUES ("Sarsen", "Whatmore", "sarsenw@bu.edu", CURRENT_DATE(), "US", "male", "test");

INSERT INTO Users(first_name, last_name, email, birth_date, hometown, gender, password)
VALUES ("A", "A", "aa@bu.edu", CURRENT_DATE(), "US", "male", "test");

INSERT INTO Users(first_name, last_name, email, birth_date, hometown, gender, password)
VALUES ("B", "A", "ba@bu.edu", CURRENT_DATE(), "US", "male", "test");

INSERT INTO Users(first_name, last_name, email, birth_date, hometown, gender, password)
VALUES ("C", "A", "ca@bu.edu", CURRENT_DATE(), "US", "male", "test");

INSERT INTO Users(first_name, last_name, email, birth_date, hometown, gender, password)
VALUES ("D", "A", "da@bu.edu", CURRENT_DATE(), "US", "male", "test");

INSERT INTO Users(first_name, last_name, email, birth_date, hometown, gender, password)
VALUES ("E", "A", "ea@bu.edu", CURRENT_DATE(), "US", "male", "test");

INSERT INTO Users(first_name, last_name, email, birth_date, hometown, gender, password)
VALUES ("F", "A", "fa@bu.edu", CURRENT_DATE(), "US", "male", "test");

INSERT INTO Users(first_name, last_name, email, birth_date, hometown, gender, password)
VALUES ("G", "A", "ga@bu.edu", CURRENT_DATE(), "US", "male", "test");

INSERT INTO Albums(albums_id, name, date, user_id)
VALUES (1, "Test_Album", CURRENT_DATE(), 1);

INSERT INTO Albums(albums_id, name, date, user_id)
VALUES (2, "Test_Album", CURRENT_DATE(), 2);

INSERT Friends(user_id1, user_id2)
VALUES (1, 2);

INSERT Friends(user_id1, user_id2)
VALUES (2, 1);

INSERT Friends(user_id1, user_id2)
VALUES (1, 3);

INSERT Friends(user_id1, user_id2)
VALUES (3, 1);

INSERT Friends(user_id1, user_id2)
VALUES (5, 2);

INSERT Friends(user_id1, user_id2)
VALUES (2, 5);

SELECT *
FROM Photos;