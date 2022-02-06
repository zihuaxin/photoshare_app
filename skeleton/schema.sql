CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Photos CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;



CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    first_name varchar(255) UNIQUE,
    last_name varchar(255) UNIQUE,
    dob varchar(255) UNIQUE,
    hometown varchar(255) UNIQUE,
    gender varchar(255) UNIQUE,
    password varchar(255),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Albums (
	album_id int4 AUTO_INCREMENT,
    album_name varchar(255),
    date_of_creation varchar(255),
    creator_id int4,
    CONSTRAINT albums_pk PRIMARY KEY (album_id)
);

CREATE TABLE Photos(
	photo_id int4 AUTO_INCREMENT,
    alblum_id int4,
    caption varchar(255),
	imgdata longblob, 
	 CONSTRAINT photos_pk PRIMARY KEY (photo_id)
);

CREATE TABLE Tags(
	tag_id int4 AUTO_INCREMENT,
	tag varchar(255),
-- how to make is so each photo has mutiple tags (*array of tag id's IDK*)
    CONSTRAINT tags_pk PRIMARY KEY (tag_id)
);

CREATE TABLE Comments(
	comment_id int4 AUTO_INCREMENT,
    text varchar(255),
    owner_id int4,
    date_of_comment varchar(255),
     CONSTRAINT comments_pk PRIMARY KEY (comment_id)
);

INSERT INTO Users (email, first_name, last_name, dob, hometown, gender, password) VALUES ('test@bu.edu', 'sarsen', 'whatmore', '2/2/2002', 'home', 'm', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
INSERT INTO Albums (album_name, date_of_creation, creator_id) VALUES ("first", "2/2/2022", (SELECT user_id FROM photoshare.users WHERE first_name = "sarsen") );
SELECT * FROM photoshare.users ;
