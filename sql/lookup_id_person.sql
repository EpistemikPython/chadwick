/*
SQLyog Community Edition- MySQL GUI v8.15 Beta1
MySQL - 5.1.28-rc-community : Database - retrosheet
*********************************************************************
*/

USE 'retrosheet';

/*Table structure for table 'lkup_id_person' */

DROP TABLE IF EXISTS 'lkup_id_person';

CREATE TABLE 'lkup_id_person' (
  'PERSON_ID' varchar(8) NOT NULL PRIMARY KEY,
  'LASTNAME' varchar(30) NOT NULL,
  'FIRSTNAME' varchar(13) DEFAULT NULL,
  'PLAYER_DEBUT' varchar(12) DEFAULT NULL,
  'MANAGER_DEBUT' varchar(12) DEFAULT NULL,
  'COACH_DEBUT' varchar(12) DEFAULT NULL,
  'UMPIRE_DEBUT' varchar(12) DEFAULT NULL,
);

/*Data for the table 'lkup_id_person' */
/* SOURCE 'ids.csv' */
load data infile "/home/marksa/dev/Retrosheet/ids.csv" into table lkup_id_person fields terminated by ',' optionally enclosed by '"' ('PERSON_ID','LASTNAME','FIRSTNAME','PLAYER_DEBUT','MANAGER_DEBUT','COACH_DEBUT','UMPIRE_DEBUT');
