/*
SQLyog Community Edition- MySQL GUI v8.15 Beta1
MySQL - 5.1.28-rc-community : Database - retrosheet
*********************************************************************
*/

-- CREATE DATABASE retrosheet;

-- USE retrosheet;


-- Table structure for table rosters
DROP TABLE IF EXISTS rosters;

-- typedef struct cw_player_struct {
  -- char *player_id, *last_name, *first_name;
  -- char bats, throws;
  -- struct cw_player_struct *prev, *next;
-- } CWPlayer;
CREATE TABLE rosters (
  PLAYER_ID varchar(8) NOT NULL,
  LAST_NAME varchar(24) NOT NULL,
  FIRST_NAME varchar(16) DEFAULT '?',
  BAT_HAND_CD char(1) NOT NULL,
  THROW_HAND_CD char(1) NOT NULL,
  TEAM_ID char(3) NOT NULL,
  POS_ID char(8) NOT NULL,
  KEY rosters_playerid_idx (PLAYER_ID)
);
