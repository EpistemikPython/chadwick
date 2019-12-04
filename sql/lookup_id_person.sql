/*
SQLyog Community Edition- MySQL GUI v8.15 Beta1
MySQL - 5.1.28-rc-community : Database - retrosheet
*********************************************************************
*/

USE retrosheet;

-- Table structure for table lkup_id_person

DROP TABLE IF EXISTS lkup_id_person;

CREATE TABLE lkup_id_person (
  PERSON_ID    varchar(8) NOT NULL PRIMARY KEY,
  LAST_NAME    varchar(32) NOT NULL,
  FIRST_NAME   varchar(16) DEFAULT NULL,
  PLAYER_DEBUT DATE DEFAULT NULL,
  MGR_DEBUT    DATE DEFAULT NULL,
  COACH_DEBUT  DATE DEFAULT NULL,
  UMP_DEBUT    DATE DEFAULT NULL
);

-- Data for the table lkup_id_person
--  SOURCE ids.csv
LOAD DATA LOCAL INFILE '/home/marksa/dev/Retrosheet/ids.csv' INTO TABLE lkup_id_person FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"';
