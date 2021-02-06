PATH already contains /home/marksa/bin
/home/marksa/.local/bin added to PATH.
/opt/bin added to PATH.
/home/marksa/opt/bin added to PATH.
/home/marksa/apps/opt/bin added to PATH.
LOADED /home/marksa/.bashals
LOADED /home/marksa/.bashfxn
getfacl: Removing leading '/' from absolute path names
Group 'marksa' ALREADY in /dev/kvm ACL.
CHECKED android_acl.sh
LOADED /home/marksa/.bashext
 _____________________________________
/ Military justice is to justice what \
| military music is to music.         |
|                                     |
\ ― Groucho Marx                      /
 -------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
/newdata/dev/git/Python/Chadwick/sql | Wed Feb 03 08:05:23 | marksa@Ares-A717-72G | bash 5.0.17 | (master)
2001 > ltf
total 636
-rw-rw-r-- 1 marksa marksa  43782 Feb  2 08:55 retrosheet-results_2021-01-29.sql
-rw-rw-r-- 1 marksa marksa   1170 Feb  2 08:53 retrosheet-queries.sql
-rw-rw-r-- 1 marksa marksa   1154 Jan 29 19:16 retrosheet-queries_2021-01-29.sql
-rw-rw-r-- 1 marksa marksa    784 Jan 29 16:34 retrosheet_rosters-table_schema.sql
-rw-rw-r-- 1 marksa marksa    405 Jan 29 16:32 rosters.sql
-rw-rw-r-- 1 marksa marksa    575 Jan 29 15:31 retrosheet-games-minutes-qry_2021-01-29.sql
-rw-rw-r-- 1 marksa marksa   2176 Dec  6  2019 wOBA.sql
-rw-rw-r-- 1 marksa marksa   8353 Dec  6  2019 linear-weights.sql
drwxrwxr-x 2 marksa marksa   4096 Dec  5  2019 exports
drwxrwxr-x 2 marksa marksa   4096 Dec  4  2019 bak
-rw-rw-r-- 1 marksa marksa    157 Dec  4  2019 mdb_2019-12-01.sql
-rw-rw-r-- 1 marksa marksa   9145 Dec  4  2019 lookup_codes.sql
-rw-rw-r-- 1 marksa marksa    793 Dec  4  2019 lookup_id_person.sql
-rw-rw-r-- 1 marksa marksa    155 Dec  4  2019 update_person_dates.sql
-rw-rw-r-- 1 marksa marksa    800 Dec  4  2019 lookup_park_code.sql
-rw-rw-r-- 1 marksa marksa   1576 Dec  4  2019 lookup_team_name.sql
-rw-rw-r-- 1 marksa marksa  25900 Dec  3  2019 subs.sql
-rw-rw-r-- 1 marksa marksa 222803 Dec  3  2019 events.sql
-rw-rw-r-- 1 marksa marksa  17130 Dec  2  2019 retrosheet_table_schema.sql
-rw-rw-r-- 1 marksa marksa 238664 Dec  1  2019 games.sql
-rw-rw-r-- 1 marksa marksa    196 Dec  1  2019 partition.sql
-rw-rw-r-- 1 marksa marksa   2362 Nov 30  2019 games-2018.sql
-rw-rw-r-- 1 marksa marksa   2235 Nov 30  2019 events-2018.sql
/newdata/dev/git/Python/Chadwick/sql | Wed Feb 03 08:14:17 | marksa@Ares-A717-72G | bash 5.0.17 | (master)
2002 > sudo mysql -u mhsatto -p
[sudo] password for marksa:          
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 35
Server version: 10.4.10-MariaDB-1:10.4.10+maria~bionic mariadb.org binary distribution

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> use retrosheet;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [retrosheet]> show tables;
+-----------------------------+
| Tables_in_retrosheet        |
+-----------------------------+
| events                      |
| events_bck                  |
| games                       |
| games_bck                   |
| lkup_cd_bases               |
| lkup_cd_battedball          |
| lkup_cd_event               |
| lkup_cd_fld                 |
| lkup_cd_hand                |
| lkup_cd_hit                 |
| lkup_cd_park_daynight       |
| lkup_cd_park_field          |
| lkup_cd_park_precip         |
| lkup_cd_park_sky            |
| lkup_cd_park_wind_direction |
| lkup_cd_recorder_method     |
| lkup_cd_recorder_pitches    |
| lkup_id_base                |
| lkup_id_home                |
| lkup_id_last                |
| lkup_id_person              |
| lkup_park_code              |
| rosters                     |
| subs                        |
+-----------------------------+
24 rows in set (0.001 sec)

MariaDB [retrosheet]> describe lkup_id_person;
ERROR 2006 (HY000): MySQL server has gone away
No connection. Trying to reconnect...
Connection id:    37
Current database: retrosheet

+--------------+-------------+------+-----+---------+-------+
| Field        | Type        | Null | Key | Default | Extra |
+--------------+-------------+------+-----+---------+-------+
| PERSON_ID    | varchar(8)  | NO   | PRI | NULL    |       |
| LAST_NAME    | varchar(32) | NO   |     | NULL    |       |
| FIRST_NAME   | varchar(16) | YES  |     | NULL    |       |
| PLAYER_DEBUT | date        | YES  |     | NULL    |       |
| MGR_DEBUT    | date        | YES  |     | NULL    |       |
| COACH_DEBUT  | date        | YES  |     | NULL    |       |
| UMP_DEBUT    | date        | YES  |     | NULL    |       |
+--------------+-------------+------+-----+---------+-------+
7 rows in set (0.098 sec)

MariaDB [retrosheet]> 
MariaDB [retrosheet]> ?

General information about MariaDB can be found at
http://mariadb.org

List of all client commands:
Note that all text commands must be first on line and end with ';'
?         (\?) Synonym for 'help'.
clear     (\c) Clear the current input statement.
connect   (\r) Reconnect to the server. Optional arguments are db and host.
delimiter (\d) Set statement delimiter.
edit      (\e) Edit command with $EDITOR.
ego       (\G) Send command to MariaDB server, display result vertically.
exit      (\q) Exit mysql. Same as quit.
go        (\g) Send command to MariaDB server.
help      (\h) Display this help.
nopager   (\n) Disable pager, print to stdout.
notee     (\t) Don''t write into outfile.
pager     (\P) Set PAGER [to_pager]. Print the query results via PAGER.
print     (\p) Print current command.
prompt    (\R) Change your mysql prompt.
quit      (\q) Quit mysql.
rehash    (\#) Rebuild completion hash.
source    (\.) Execute an SQL script file. Takes a file name as an argument.
status    (\s) Get status information from the server.
system    (\!) Execute a system shell command.
tee       (\T) Set outfile [to_outfile]. Append everything into given outfile.
use       (\u) Use another database. Takes database name as argument.
charset   (\C) Switch to another charset. Might be needed for processing binlog with multi-byte charsets.
warnings  (\W) Show warnings after every statement.
nowarning (\w) Don''t show warnings after every statement.

For server side help, type 'help contents'

MariaDB [retrosheet]> describe events;
ERROR 2006 (HY000): MySQL server has gone away
No connection. Trying to reconnect...
Connection id:    39
Current database: retrosheet

+---------------------------+---------------------+------+-----+---------+----------------+
| Field                     | Type                | Null | Key | Default | Extra          |
+---------------------------+---------------------+------+-----+---------+----------------+
| seq_events                | int(11) unsigned    | NO   | PRI | NULL    | auto_increment |
| GAME_ID                   | char(12)            | NO   | MUL | NULL    |                |
| YEAR_ID                   | year(4)             | NO   |     | 2102    |                |
| AWAY_TEAM_ID              | char(3)             | NO   |     | NULL    |                |
| INN_CT                    | tinyint(2) unsigned | NO   |     | NULL    |                |
| BAT_HOME_ID               | tinyint(1) unsigned | NO   |     | NULL    |                |
| OUTS_CT                   | tinyint(1) unsigned | NO   |     | NULL    |                |
| BALLS_CT                  | tinyint(1) unsigned | NO   |     | NULL    |                |
| STRIKES_CT                | tinyint(1) unsigned | NO   |     | NULL    |                |
| PITCH_SEQ_TX              | varchar(255)        | NO   |     | NULL    |                |
| AWAY_SCORE_CT             | tinyint(2) unsigned | NO   |     | NULL    |                |
| HOME_SCORE_CT             | tinyint(2) unsigned | NO   |     | NULL    |                |
| BAT_ID                    | char(8)             | NO   |     | NULL    |                |
| BAT_HAND_CD               | char(1)             | NO   |     | NULL    |                |
| RESP_BAT_ID               | char(8)             | NO   |     | NULL    |                |
| RESP_BAT_HAND_CD          | char(1)             | NO   |     | NULL    |                |
| PIT_ID                    | char(8)             | NO   |     | NULL    |                |
| PIT_HAND_CD               | char(1)             | NO   |     | NULL    |                |
| RES_PIT_ID                | char(8)             | NO   |     | NULL    |                |
| RES_PIT_HAND_CD           | char(1)             | NO   |     | NULL    |                |
| POS2_FLD_ID               | char(8)             | NO   |     | NULL    |                |
| POS3_FLD_ID               | char(8)             | NO   |     | NULL    |                |
| POS4_FLD_ID               | char(8)             | NO   |     | NULL    |                |
| POS5_FLD_ID               | char(8)             | NO   |     | NULL    |                |
| POS6_FLD_ID               | char(8)             | NO   |     | NULL    |                |
| POS7_FLD_ID               | char(8)             | NO   |     | NULL    |                |
| POS8_FLD_ID               | char(8)             | NO   |     | NULL    |                |
| POS9_FLD_ID               | char(8)             | NO   |     | NULL    |                |
| BASE1_RUN_ID              | varchar(8)          | NO   |     | NULL    |                |
| BASE2_RUN_ID              | varchar(8)          | NO   |     | NULL    |                |
| BASE3_RUN_ID              | varchar(8)          | NO   |     | NULL    |                |
| EVENT_TX                  | varchar(255)        | NO   |     | NULL    |                |
| LEADOFF_FL                | char(1)             | NO   |     | NULL    |                |
| PH_FL                     | char(1)             | NO   |     | NULL    |                |
| BAT_FLD_CD                | tinyint(1) unsigned | NO   |     | NULL    |                |
| BAT_LINEUP_ID             | tinyint(2) unsigned | NO   |     | NULL    |                |
| EVENT_CD                  | tinyint(2) unsigned | NO   |     | NULL    |                |
| BAT_EVENT_FL              | char(1)             | NO   |     | NULL    |                |
| AB_FL                     | char(1)             | NO   |     | NULL    |                |
| H_CD                      | tinyint(1) unsigned | NO   |     | NULL    |                |
| SH_FL                     | char(1)             | NO   |     | NULL    |                |
| SF_FL                     | char(1)             | NO   |     | NULL    |                |
| EVENT_OUTS_CT             | tinyint(1) unsigned | NO   |     | NULL    |                |
| DP_FL                     | char(1)             | NO   |     | NULL    |                |
| TP_FL                     | char(1)             | NO   |     | NULL    |                |
| RBI_CT                    | tinyint(1) unsigned | NO   |     | NULL    |                |
| WP_FL                     | char(1)             | NO   |     | NULL    |                |
| PB_FL                     | char(1)             | NO   |     | NULL    |                |
| FLD_CD                    | tinyint(2) unsigned | NO   |     | NULL    |                |
| BATTEDBALL_CD             | char(1)             | NO   |     | NULL    |                |
| BUNT_FL                   | char(1)             | NO   |     | NULL    |                |
| FOUL_FL                   | char(1)             | NO   |     | NULL    |                |
| BATTEDBALL_LOC_TX         | varchar(5)          | NO   |     | NULL    |                |
| ERR_CT                    | tinyint(1) unsigned | NO   |     | NULL    |                |
| ERR1_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| ERR1_CD                   | char(1)             | NO   |     | NULL    |                |
| ERR2_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| ERR2_CD                   | char(1)             | NO   |     | NULL    |                |
| ERR3_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| ERR3_CD                   | char(1)             | NO   |     | NULL    |                |
| BAT_DEST_ID               | tinyint(1) unsigned | NO   |     | NULL    |                |
| RUN1_DEST_ID              | tinyint(1) unsigned | NO   |     | NULL    |                |
| RUN2_DEST_ID              | tinyint(1) unsigned | NO   |     | NULL    |                |
| RUN3_DEST_ID              | tinyint(1) unsigned | NO   |     | NULL    |                |
| BAT_PLAY_TX               | varchar(8)          | NO   |     | NULL    |                |
| RUN1_PLAY_TX              | varchar(255)        | NO   |     | NULL    |                |
| RUN2_PLAY_TX              | varchar(255)        | NO   |     | NULL    |                |
| RUN3_PLAY_TX              | varchar(255)        | NO   |     | NULL    |                |
| RUN1_SB_FL                | char(1)             | NO   |     | NULL    |                |
| RUN2_SB_FL                | char(1)             | NO   |     | NULL    |                |
| RUN3_SB_FL                | char(1)             | NO   |     | NULL    |                |
| RUN1_CS_FL                | char(1)             | NO   |     | NULL    |                |
| RUN2_CS_FL                | char(1)             | NO   |     | NULL    |                |
| RUN3_CS_FL                | char(1)             | NO   |     | NULL    |                |
| RUN1_PK_FL                | char(1)             | NO   |     | NULL    |                |
| RUN2_PK_FL                | char(1)             | NO   |     | NULL    |                |
| RUN3_PK_FL                | char(1)             | NO   |     | NULL    |                |
| RUN1_RESP_PIT_ID          | varchar(8)          | NO   |     | NULL    |                |
| RUN2_RESP_PIT_ID          | varchar(8)          | NO   |     | NULL    |                |
| RUN3_RESP_PIT_ID          | varchar(8)          | NO   |     | NULL    |                |
| GAME_NEW_FL               | char(1)             | NO   |     | NULL    |                |
| GAME_END_FL               | char(1)             | NO   |     | NULL    |                |
| PR_RUN1_FL                | char(1)             | NO   |     | NULL    |                |
| PR_RUN2_FL                | char(1)             | NO   |     | NULL    |                |
| PR_RUN3_FL                | char(1)             | NO   |     | NULL    |                |
| REMOVED_FOR_PR_RUN1_ID    | varchar(8)          | NO   |     | NULL    |                |
| REMOVED_FOR_PR_RUN2_ID    | varchar(8)          | NO   |     | NULL    |                |
| REMOVED_FOR_PR_RUN3_ID    | varchar(8)          | NO   |     | NULL    |                |
| REMOVED_FOR_PH_BAT_ID     | varchar(8)          | NO   |     | NULL    |                |
| REMOVED_FOR_PH_BAT_FLD_CD | tinyint(2) unsigned | NO   |     | NULL    |                |
| PO1_FLD_CD                | tinyint(2) unsigned | NO   |     | NULL    |                |
| PO2_FLD_CD                | tinyint(2) unsigned | NO   |     | NULL    |                |
| PO3_FLD_CD                | tinyint(2) unsigned | NO   |     | NULL    |                |
| ASS1_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| ASS2_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| ASS3_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| ASS4_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| ASS5_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| EVENT_ID                  | tinyint(3) unsigned | NO   |     | NULL    |                |
| HOME_TEAM_ID              | char(3)             | NO   |     | NULL    |                |
| BAT_TEAM_ID               | char(3)             | NO   |     | NULL    |                |
| FLD_TEAM_ID               | char(3)             | NO   |     | NULL    |                |
| BAT_LAST_ID               | tinyint(1) unsigned | NO   |     | NULL    |                |
| INN_NEW_FL                | char(1)             | NO   |     | NULL    |                |
| INN_END_FL                | char(1)             | NO   |     | NULL    |                |
| START_BAT_SCORE_CT        | tinyint(2) unsigned | NO   |     | NULL    |                |
| START_FLD_SCORE_CT        | tinyint(2) unsigned | NO   |     | NULL    |                |
| INN_RUNS_CT               | tinyint(2) unsigned | NO   |     | NULL    |                |
| GAME_PA_CT                | tinyint(3) unsigned | NO   |     | NULL    |                |
| INN_PA_CT                 | tinyint(2) unsigned | NO   |     | NULL    |                |
| PA_NEW_FL                 | char(1)             | NO   |     | NULL    |                |
| PA_TRUNC_FL               | char(1)             | NO   |     | NULL    |                |
| START_BASES_CD            | tinyint(1) unsigned | NO   |     | NULL    |                |
| END_BASES_CD              | tinyint(1) unsigned | NO   |     | NULL    |                |
| BAT_START_FL              | char(1)             | NO   |     | NULL    |                |
| RESP_BAT_START_FL         | char(1)             | NO   |     | NULL    |                |
| BATTER_ON_DECK_ID         | varchar(8)          | NO   |     | NULL    |                |
| BATTER_IN_HOLE_ID         | varchar(8)          | NO   |     | NULL    |                |
| PIT_START_FL              | char(1)             | NO   |     | NULL    |                |
| RESP_PIT_START_FL         | char(1)             | NO   |     | NULL    |                |
| RUN1_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN1_LINEUP_ID            | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN1_ORIGIN_EVENT_ID      | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN2_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN2_LINEUP_ID            | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN2_ORIGIN_EVENT_ID      | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN3_FLD_CD               | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN3_LINEUP_ID            | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN3_ORIGIN_EVENT_ID      | tinyint(2) unsigned | NO   |     | NULL    |                |
| RUN1_RESP_CATCH_ID        | varchar(8)          | NO   |     | NULL    |                |
| RUN2_RESP_CATCH_ID        | varchar(8)          | NO   |     | NULL    |                |
| RUN3_RESP_CATCH_ID        | varchar(8)          | NO   |     | NULL    |                |
| PA_BALL_CT                | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_CALLED_BALL_CT         | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_INTENT_BALL_CT         | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_PITCHOUT_BALL_CT       | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_HIT_BALL_CT            | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_OTHER_BALL_CT          | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_STRIKE_CT              | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_CALLED_STRIKE_CT       | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_SWINGMISS_STRIKE_CT    | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_FOUL_STRIKE_CT         | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_BIP_STRIKE_CT          | tinyint(1) unsigned | NO   |     | NULL    |                |
| PA_OTHER_STRIKE_CT        | tinyint(1) unsigned | NO   |     | NULL    |                |
| EVENT_RUNS_CT             | tinyint(1) unsigned | NO   |     | NULL    |                |
| FLD_ID                    | varchar(8)          | NO   |     | NULL    |                |
| BASE2_FORCE_FL            | char(1)             | NO   |     | NULL    |                |
| BASE3_FORCE_FL            | char(1)             | NO   |     | NULL    |                |
| BASE4_FORCE_FL            | char(1)             | NO   |     | NULL    |                |
| BAT_SAFE_ERR_FL           | char(1)             | NO   |     | NULL    |                |
| BAT_FATE_ID               | tinyint(1) unsigned | NO   |     | NULL    |                |
| RUN1_FATE_ID              | tinyint(1) unsigned | NO   |     | NULL    |                |
| RUN2_FATE_ID              | tinyint(1) unsigned | NO   |     | NULL    |                |
| RUN3_FATE_ID              | tinyint(1) unsigned | NO   |     | NULL    |                |
| FATE_RUNS_CT              | tinyint(1) unsigned | NO   |     | NULL    |                |
| ASS6_FLD_CD               | tinyint(1) unsigned | NO   |     | NULL    |                |
| ASS7_FLD_CD               | tinyint(1) unsigned | NO   |     | NULL    |                |
| ASS8_FLD_CD               | tinyint(1) unsigned | NO   |     | NULL    |                |
| ASS9_FLD_CD               | tinyint(1) unsigned | NO   |     | NULL    |                |
| ASS10_FLD_CD              | tinyint(1) unsigned | NO   |     | NULL    |                |
| UNCERTAIN_PLAY_EXC_FL     | varchar(1)          | YES  |     | NULL    |                |
| UNKNOWN_OUT_EXC_FL        | varchar(1)          | YES  |     | NULL    |                |
+---------------------------+---------------------+------+-----+---------+----------------+
162 rows in set (0.217 sec)

MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', BAT_ID AS 'Batter', SUM(RBI_CT) AS 'RBIs' 
    -> FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT >= 1 
    -> GROUP BY GAME_ID ORDER BY GAME_ID DESC;
^CCtrl-C -- query killed. Continuing normally.
ERROR 1317 (70100): Query execution was interrupted
MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', SUM(EVENT_RUNS_CT) AS 'Runs'  FROM events WHERE YEAR_ID = '1955' AND BAT_ID = 'aaroh101' AND EVENT_RUNS_CT >= 1  GROUP BY GAME_ID ORDER BY GAME_ID DESC;
+--------------+------+
| Game         | Runs |
+--------------+------+
| SLN195509250 |    2 |
| SLN195508180 |    2 |
| SLN195508160 |    1 |
| SLN195508150 |    1 |
| SLN195505080 |    2 |
| SLN195505070 |    1 |
| SLN195505060 |    1 |
| PIT195507210 |    1 |
| PIT195506110 |    1 |
| PIT195505040 |    1 |
| PHI195507140 |    1 |
| PHI195506052 |    1 |
| PHI195506030 |    1 |
| PHI195504300 |    1 |
| NY1195507171 |    1 |
| NY1195507160 |    2 |
| NY1195506080 |    1 |
| NY1195506070 |    3 |
| NY1195504270 |    1 |
| NY1195504260 |    1 |
| MLN195509180 |    1 |
| MLN195509140 |    2 |
| MLN195509112 |    1 |
| MLN195509040 |    3 |
| MLN195508200 |    5 |
| MLN195508190 |    2 |
| MLN195508111 |    1 |
| MLN195508071 |    2 |
| MLN195508040 |    1 |
| MLN195508030 |    1 |
| MLN195507300 |    1 |
| MLN195507290 |    1 |
| MLN195507280 |    1 |
| MLN195507260 |    2 |
| MLN195507101 |    1 |
| MLN195507082 |    2 |
| MLN195507042 |    1 |
| MLN195506290 |    3 |
| MLN195506280 |    2 |
| MLN195506240 |    4 |
| MLN195506190 |    2 |
| MLN195506180 |    1 |
| MLN195506170 |    2 |
| MLN195505260 |    1 |
| MLN195505250 |    1 |
| MLN195505190 |    1 |
| MLN195505180 |    1 |
| MLN195505140 |    1 |
| MLN195505130 |    1 |
| MLN195505120 |    1 |
| MLN195504230 |    1 |
| MLN195504190 |    1 |
| MLN195504120 |    1 |
| CIN195507030 |    1 |
| CIN195507020 |    3 |
| CIN195505302 |    1 |
| CIN195504172 |    1 |
| CIN195504171 |    1 |
| CIN195504160 |    1 |
| CHN195508140 |    1 |
| CHN195505280 |    1 |
| BRO195509010 |    1 |
| BRO195508310 |    2 |
| BRO195507242 |    4 |
| BRO195507241 |    2 |
| BRO195507220 |    1 |
| BRO195506010 |    1 |
| BRO195505010 |    1 |
+--------------+------+
68 rows in set (56 min 13.795 sec)

MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', SUM(EVENT_RUNS_CT) AS 'Runs' FROM events WHERE YEAR_ID = '1955' AND BAT_ID = 'aaroh101' AND EVENT_RUNS_CT >= 1 GROUP BY GAME_ID ORDER BY SUM(EVENT_RUNS_CT) DESC;
+--------------+------+
| Game         | Runs |
+--------------+------+
| MLN195508200 |    5 |
| BRO195507242 |    4 |
| MLN195506240 |    4 |
| CIN195507020 |    3 |
| MLN195506290 |    3 |
| NY1195506070 |    3 |
| MLN195509040 |    3 |
| BRO195508310 |    2 |
| MLN195506170 |    2 |
| MLN195506280 |    2 |
| MLN195507260 |    2 |
| MLN195508190 |    2 |
| MLN195509140 |    2 |
| SLN195508180 |    2 |
| BRO195507241 |    2 |
| MLN195506190 |    2 |
| SLN195505080 |    2 |
| SLN195509250 |    2 |
| MLN195507082 |    2 |
| MLN195508071 |    2 |
| NY1195507160 |    2 |
| BRO195506010 |    1 |
| CIN195504160 |    1 |
| MLN195504230 |    1 |
| MLN195505180 |    1 |
| MLN195507101 |    1 |
| MLN195507300 |    1 |
| MLN195508111 |    1 |
| MLN195509112 |    1 |
| NY1195504270 |    1 |
| NY1195507171 |    1 |
| PHI195507140 |    1 |
| SLN195505060 |    1 |
| SLN195508160 |    1 |
| BRO195507220 |    1 |
| BRO195509010 |    1 |
| CIN195504171 |    1 |
| CIN195507030 |    1 |
| MLN195505120 |    1 |
| MLN195505190 |    1 |
| MLN195506180 |    1 |
| MLN195508030 |    1 |
| PHI195504300 |    1 |
| PIT195505040 |    1 |
| SLN195505070 |    1 |
| CHN195505280 |    1 |
| CIN195504172 |    1 |
| MLN195504120 |    1 |
| MLN195505130 |    1 |
| MLN195505250 |    1 |
| MLN195507042 |    1 |
| MLN195507280 |    1 |
| MLN195508040 |    1 |
| MLN195509180 |    1 |
| NY1195506080 |    1 |
| PHI195506030 |    1 |
| PIT195506110 |    1 |
| BRO195505010 |    1 |
| CHN195508140 |    1 |
| CIN195505302 |    1 |
| MLN195504190 |    1 |
| MLN195505140 |    1 |
| MLN195505260 |    1 |
| MLN195507290 |    1 |
| NY1195504260 |    1 |
| PHI195506052 |    1 |
| PIT195507210 |    1 |
| SLN195508150 |    1 |
+--------------+------+
68 rows in set (14 min 45.269 sec)

MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', SUM(EVENT_RUNS_CT) AS 'Runs' FROM events WHERE YEAR_ID = '1955' AND BAT_ID = 'aaroh101' AND EVENT_RUNS_CT >= 1 GROUP BY YEAR_ID;
+--------------+------+
| Game         | Runs |
+--------------+------+
| MLN195504190 |  100 |
+--------------+------+
1 row in set (2 min 54.884 sec)

MariaDB [retrosheet]>