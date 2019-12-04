/*
SQLyog Community Edition- MySQL GUI v8.15 Beta1
MySQL - 5.1.28-rc-community : Database - retrosheet
*********************************************************************
*/

USE retrosheet;


CREATE TABLE lkup_park_code (
    PK_ID    varchar(8) NOT NULL PRIMARY KEY,
    PK_NAME  varchar(255) DEFAULT NULL,
    PK_AKA   varchar(255) DEFAULT NULL,
    CITY     varchar(32) DEFAULT NULL,
    STATE    varchar(32) DEFAULT NULL,
    START_DT DATE DEFAULT NULL,
    END_DT   DATE DEFAULT NULL,
    LEAGUE   varchar(8) DEFAULT NULL,
    NOTES    varchar(255) DEFAULT NULL
);

-- Data for the table lkup_park_code
--  SOURCE ids.csv
LOAD DATA LOCAL INFILE '/home/marksa/dev/Retrosheet/park_codes.csv' INTO TABLE lkup_park_code FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
