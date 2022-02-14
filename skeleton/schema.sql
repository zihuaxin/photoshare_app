CREATE DATABASE IF NOT EXISTS photoshare;

USE photoshare;

DROP TABLE IF EXISTS album_user CASCADE;
DROP TABLE IF EXISTS photo_tags CASCADE;
DROP TABLE IF EXISTS user_comment CASCADE;
DROP TABLE IF EXISTS album_photo CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;

# ENTITIES

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    first_name varchar(255),
    last_name varchar(255),
    dob DATE, # probably better as DATE
    hometown varchar(255),
    gender INTEGER, # 0: male, 1: female, 2: others?
    password varchar(255) UNIQUE,
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);

# symmetrical friendship
CREATE TABLE Friends (
     user_id1 INT NOT NULL REFERENCES Users(user_id),
     user_id2 INT NOT NULL REFERENCES Users(user_id),
     CONSTRAINT PK_Friends_user_id1_user_id2 PRIMARY KEY (user_id1, user_id2),
     CONSTRAINT UQ_Friends_user_id1_user_id2 UNIQUE (user_id2, user_id1)
);

# not sure if this is duplicate of Photos
/*
CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);
*/

CREATE TABLE Albums (
	album_id int4 AUTO_INCREMENT,
    album_name varchar(255),
    date_of_creation DATE,
    CONSTRAINT albums_pk PRIMARY KEY (album_id)
);

CREATE TABLE album_photo (
	photo_id int4 AUTO_INCREMENT,
    caption varchar(255),
	imgdata longblob, 
    album_id int4  NOT NULL,
    PRIMARY KEY (photo_id, album_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

CREATE TABLE Tags(
	tag_id int4 AUTO_INCREMENT,
    
    # NOTE: lower case constraint needs to be added during insertion
	tag_name varchar(255) UNIQUE,
    
    CONSTRAINT tags_pk PRIMARY KEY (tag_id)
);

CREATE TABLE Comments(
	comment_id int4 AUTO_INCREMENT,
    text varchar(255),
    date_of_comment DATE,
     CONSTRAINT comments_pk PRIMARY KEY (comment_id)
);

# RELATIONSHIPS

# one to many
# participation constraint?
CREATE TABLE album_user (
	user_id int4,
    album_id int4,
    PRIMARY KEY (album_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

# many to many
# no participation constraints
CREATE TABLE photo_tags (
	photo_id int4,
    tag_id int4,
    PRIMARY KEY (photo_id, tag_id),
    FOREIGN KEY (photo_id) REFERENCES album_photo(photo_id),
    FOREIGN KEY (tag_id) REFERENCES Tags(tag_id)
);

# one to many
# no participation constraints? (user can be banned but their comments can be left behind )
CREATE TABLE user_comment(
	user_id int4,
    comment_id int4,
    PRIMARY KEY (comment_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (comment_id) REFERENCES Comments(comment_id)
);

INSERT INTO Users (email, first_name, last_name, dob, hometown, gender, password) VALUES ('test@bu.edu', 'sarsen', 'whatmore', '1997-06-10', 'home', 0, 'test0');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test1');
INSERT INTO Albums (album_name, date_of_creation) VALUES ("first", '1997-06-10');
INSERT INTO Tags (tag_name) VALUES ("Boston");

SELECT tag_name FROM photoshare.tags ;
