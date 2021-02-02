
/newdata/dev/git/Python/Chadwick/sql | Fri Jan 29 14:53:27 | marksa@Ares-A717-72G | bash 5.0.17 | (master)
2001 > sudo mysql -u mhsatto -p
[sudo] password for marksa:        
Sorry, try again.
[sudo] password for marksa: 
< marksa pswd for sudo >
Enter password: 
< mhsatto pswd for mysql >
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 46
Server version: 10.4.10-MariaDB-1:10.4.10+maria~bionic mariadb.org binary distribution

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> use retrosheet
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [retrosheet]> show tables
    -> ;
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
| subs                        |
+-----------------------------+
23 rows in set (0.001 sec)

MariaDB [retrosheet]> SELECT GAME_ID, AWAY_TEAM_ID, HOME_TEAM_ID, AWAY_SCORE_CT, HOME_SCORE_CT, INN_CT, MINUTES_GAME_CT 
    -> FROM games 
    -> WHERE INN_CT = 9
    -> ORDER BY MINUTES_GAME_CT DESC
    -> LIMIT 50;
+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
| GAME_ID      | AWAY_TEAM_ID | HOME_TEAM_ID | AWAY_SCORE_CT | HOME_SCORE_CT | INN_CT | MINUTES_GAME_CT |
+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
| BOS200608182 | NYA          | BOS          |            14 |            11 |      9 |             285 |
| BOS200709140 | NYA          | BOS          |             8 |             7 |      9 |             283 |
| TEX201709010 | ANA          | TEX          |             9 |            10 |      9 |             273 |
| BOS201705140 | TBA          | BOS          |            11 |             2 |      9 |             272 |
| NYA201108250 | OAK          | NYA          |             9 |            22 |      9 |             271 |
| COL201606240 | ARI          | COL          |            10 |             9 |      9 |             270 |
| PIT201807060 | PHI          | PIT          |            17 |             5 |      9 |             270 |
| SFN200110050 | LAN          | SFN          |            11 |            10 |      9 |             267 |
| NYA201005290 | CLE          | NYA          |            13 |            11 |      9 |             262 |
| CHN200005110 | MIL          | CHN          |            14 |             8 |      9 |             262 |
| WAS201710010 | PIT          | WAS          |            11 |             8 |      9 |             262 |
| NYA199709050 | BAL          | NYA          |            13 |             9 |      9 |             262 |
| BAL199604300 | NYA          | BAL          |            13 |            10 |      9 |             261 |
| BOS201109010 | NYA          | BOS          |             4 |             2 |      9 |             261 |
| BOS200904250 | NYA          | BOS          |            11 |            16 |      9 |             261 |
| TEX200008310 | CLE          | TEX          |             7 |            14 |      9 |             261 |
| COL199606300 | LAN          | COL          |            15 |            16 |      9 |             260 |
| CHA199704050 | DET          | CHA          |            15 |            12 |      9 |             260 |
| BAL199605170 | SEA          | BAL          |            13 |            14 |      9 |             260 |
| LAN201706250 | COL          | LAN          |             6 |            12 |      9 |             259 |
| MIN201707230 | DET          | MIN          |             9 |             6 |      9 |             259 |
| CLE200904280 | BOS          | CLE          |             8 |             9 |      9 |             259 |
| COL200004162 | SLN          | COL          |            13 |            14 |      9 |             259 |
| BOS201407020 | CHN          | BOS          |            16 |             9 |      9 |             259 |
| LAN196210020 | SFN          | LAN          |             7 |             8 |      9 |             258 |
| CHA201508290 | SEA          | CHA          |             7 |             6 |      9 |             256 |
| BAL200509270 | NYA          | BAL          |             9 |            17 |      9 |             256 |
| CLE201504110 | DET          | CLE          |             9 |             6 |      9 |             256 |
| KCA201409160 | CHA          | KCA          |             7 |             5 |      9 |             256 |
| NYA198606080 | BAL          | NYA          |            18 |             9 |      9 |             256 |
| BOS201604210 | TBA          | BOS          |            12 |             8 |      9 |             256 |
| TEX201009110 | NYA          | TEX          |             6 |             7 |      9 |             256 |
| TBA200205310 | OAK          | TBA          |            13 |             9 |      9 |             255 |
| OAK201206230 | SFN          | OAK          |             9 |             8 |      9 |             255 |
| TOR198804110 | NYA          | TOR          |             9 |            17 |      9 |             255 |
| BOS201608100 | NYA          | BOS          |             9 |             4 |      9 |             255 |
| TEX199604190 | BAL          | TEX          |             7 |            26 |      9 |             255 |
| WAS201809230 | NYN          | WAS          |             8 |             6 |      9 |             254 |
| LAN201507060 | PHI          | LAN          |             7 |            10 |      9 |             253 |
| BRO194508140 | SLN          | BRO          |             2 |             1 |      9 |             253 |
| MIL201109260 | PIT          | MIL          |             9 |             8 |      9 |             253 |
| DET201708240 | NYA          | DET          |             6 |            10 |      9 |             253 |
| COL200006280 | SFN          | COL          |            13 |            17 |      9 |             252 |
| NYA200507040 | BAL          | NYA          |             8 |            13 |      9 |             252 |
| NYA199808250 | ANA          | NYA          |             7 |             6 |      9 |             252 |
| BOS200204010 | TOR          | BOS          |            12 |            11 |      9 |             252 |
| BOS201308180 | NYA          | BOS          |             9 |             6 |      9 |             252 |
| ANA201708060 | OAK          | ANA          |            11 |            10 |      9 |             252 |
| DET199309150 | TOR          | DET          |            14 |             8 |      9 |             252 |
| CHA198307100 | MIL          | CHA          |            12 |             9 |      9 |             251 |
+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
50 rows in set (0.112 sec)

MariaDB [retrosheet]> SELECT GAME_ID, AWAY_TEAM_ID, HOME_TEAM_ID, AWAY_SCORE_CT, HOME_SCORE_CT, INN_CT, MINUTES_GAME_CT  FROM games  WHERE INN_CT = 9 AND MINUTES_GAME_CT >= 250 ORDER BY MINUTES_GAME_CT DESC;
+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
| GAME_ID      | AWAY_TEAM_ID | HOME_TEAM_ID | AWAY_SCORE_CT | HOME_SCORE_CT | INN_CT | MINUTES_GAME_CT |
+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
| BOS200608182 | NYA          | BOS          |            14 |            11 |      9 |             285 |
| BOS200709140 | NYA          | BOS          |             8 |             7 |      9 |             283 |
| TEX201709010 | ANA          | TEX          |             9 |            10 |      9 |             273 |
| BOS201705140 | TBA          | BOS          |            11 |             2 |      9 |             272 |
| NYA201108250 | OAK          | NYA          |             9 |            22 |      9 |             271 |
| COL201606240 | ARI          | COL          |            10 |             9 |      9 |             270 |
| PIT201807060 | PHI          | PIT          |            17 |             5 |      9 |             270 |
| SFN200110050 | LAN          | SFN          |            11 |            10 |      9 |             267 |
| WAS201710010 | PIT          | WAS          |            11 |             8 |      9 |             262 |
| NYA201005290 | CLE          | NYA          |            13 |            11 |      9 |             262 |
| CHN200005110 | MIL          | CHN          |            14 |             8 |      9 |             262 |
| NYA199709050 | BAL          | NYA          |            13 |             9 |      9 |             262 |
| TEX200008310 | CLE          | TEX          |             7 |            14 |      9 |             261 |
| BOS200904250 | NYA          | BOS          |            11 |            16 |      9 |             261 |
| BOS201109010 | NYA          | BOS          |             4 |             2 |      9 |             261 |
| BAL199604300 | NYA          | BAL          |            13 |            10 |      9 |             261 |
| BAL199605170 | SEA          | BAL          |            13 |            14 |      9 |             260 |
| COL199606300 | LAN          | COL          |            15 |            16 |      9 |             260 |
| CHA199704050 | DET          | CHA          |            15 |            12 |      9 |             260 |
| LAN201706250 | COL          | LAN          |             6 |            12 |      9 |             259 |
| MIN201707230 | DET          | MIN          |             9 |             6 |      9 |             259 |
| COL200004162 | SLN          | COL          |            13 |            14 |      9 |             259 |
| CLE200904280 | BOS          | CLE          |             8 |             9 |      9 |             259 |
| BOS201407020 | CHN          | BOS          |            16 |             9 |      9 |             259 |
| LAN196210020 | SFN          | LAN          |             7 |             8 |      9 |             258 |
| CHA201508290 | SEA          | CHA          |             7 |             6 |      9 |             256 |
| CLE201504110 | DET          | CLE          |             9 |             6 |      9 |             256 |
| TEX201009110 | NYA          | TEX          |             6 |             7 |      9 |             256 |
| KCA201409160 | CHA          | KCA          |             7 |             5 |      9 |             256 |
| BAL200509270 | NYA          | BAL          |             9 |            17 |      9 |             256 |
| NYA198606080 | BAL          | NYA          |            18 |             9 |      9 |             256 |
| BOS201604210 | TBA          | BOS          |            12 |             8 |      9 |             256 |
| BOS201608100 | NYA          | BOS          |             9 |             4 |      9 |             255 |
| TOR198804110 | NYA          | TOR          |             9 |            17 |      9 |             255 |
| TEX199604190 | BAL          | TEX          |             7 |            26 |      9 |             255 |
| OAK201206230 | SFN          | OAK          |             9 |             8 |      9 |             255 |
| TBA200205310 | OAK          | TBA          |            13 |             9 |      9 |             255 |
| WAS201809230 | NYN          | WAS          |             8 |             6 |      9 |             254 |
| LAN201507060 | PHI          | LAN          |             7 |            10 |      9 |             253 |
| MIL201109260 | PIT          | MIL          |             9 |             8 |      9 |             253 |
| DET201708240 | NYA          | DET          |             6 |            10 |      9 |             253 |
| BRO194508140 | SLN          | BRO          |             2 |             1 |      9 |             253 |
| NYA200507040 | BAL          | NYA          |             8 |            13 |      9 |             252 |
| BOS200204010 | TOR          | BOS          |            12 |            11 |      9 |             252 |
| COL200006280 | SFN          | COL          |            13 |            17 |      9 |             252 |
| DET199309150 | TOR          | DET          |            14 |             8 |      9 |             252 |
| NYA199808250 | ANA          | NYA          |             7 |             6 |      9 |             252 |
| ANA201708060 | OAK          | ANA          |            11 |            10 |      9 |             252 |
| BOS201308180 | NYA          | BOS          |             9 |             6 |      9 |             252 |
| CHA198307100 | MIL          | CHA          |            12 |             9 |      9 |             251 |
| SDN201705050 | LAN          | SDN          |             8 |             2 |      9 |             251 |
| ARI201604040 | COL          | ARI          |            10 |             5 |      9 |             251 |
| BOS199105150 | CHA          | BOS          |             6 |             9 |      9 |             251 |
| BOS201607230 | MIN          | BOS          |            11 |             9 |      9 |             251 |
| TBA201405090 | CLE          | TBA          |             6 |             3 |      9 |             250 |
| DET199108140 | CHA          | DET          |             9 |             8 |      9 |             250 |
| WAS201809040 | SLN          | WAS          |            11 |             8 |      9 |             250 |
| MIN201408240 | DET          | MIN          |            13 |             4 |      9 |             250 |
| FLO199607270 | SDN          | FLO          |            20 |            12 |      9 |             250 |
| LAN201808200 | SLN          | LAN          |             5 |             3 |      9 |             250 |
| CLE199606220 | NYA          | CLE          |            11 |             9 |      9 |             250 |
+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
61 rows in set (0.101 sec)

MariaDB [retrosheet]> SELECT `GAME_ID` AS 'Game',`PIT_ID` AS 'Pitcher',COUNT(*) AS 'Strikeouts'
    -> FROM `events` 
    -> WHERE `PIT_ID` = 'clemr001' 
    -> AND `EVENT_CD` = '3'
    -> GROUP BY `GAME_ID`
    -> ORDER BY COUNT(*) DESC;

;
^CCtrl-C -- query killed. Continuing normally.
ERROR 1317 (70100): Query execution was interrupted
MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', PIT_ID AS 'Pitcher', COUNT(*) AS 'Strikeouts' FROM events  WHERE PIT_ID = 'clemr001'  AND EVENT_CD = '3' GROUP BY GAME_ID ORDER BY COUNT(*) DESC;
^CCtrl-C -- query killed. Continuing normally.
ERROR 1317 (70100): Query execution was interrupted
MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', PIT_ID AS 'Pitcher', COUNT(*) AS 'Strikeouts' FROM events  WHERE PIT_ID = 'clemr001'  AND EVENT_CD = '3' GROUP BY GAME_ID ORDER BY COUNT(*) DESC LIMIT 50;
ERROR 1053 (08S01): Server shutdown in progress
MariaDB [retrosheet]> SELECT GAME_ID, AWAY_TEAM_ID, HOME_TEAM_ID, AWAY_SCORE_CT, HOME_SCORE_CT, INN_CT, MINUTES_GAME_CT FROM games WHERE INN_CT = 9 AND ( HOME_TEAM_ID = 'TOR' OR AWAY_TEAM_ID = 'TOR' ) ORDER BY MINUTES_GAME_CT DESC LIMIT 50;
ERROR 2006 (HY000): MySQL server has gone away
No connection. Trying to reconnect...
Connection id:    35
Current database: retrosheet

+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
| GAME_ID      | AWAY_TEAM_ID | HOME_TEAM_ID | AWAY_SCORE_CT | HOME_SCORE_CT | INN_CT | MINUTES_GAME_CT |
+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
| TOR198804110 | NYA          | TOR          |             9 |            17 |      9 |             255 |
| BOS200204010 | TOR          | BOS          |            12 |            11 |      9 |             252 |
| DET199309150 | TOR          | DET          |            14 |             8 |      9 |             252 |
| NYA200304140 | TOR          | NYA          |             9 |            10 |      9 |             248 |
| TBA200907080 | TOR          | TBA          |             9 |            10 |      9 |             245 |
| TOR198707250 | MIN          | TOR          |            13 |             9 |      9 |             245 |
| TOR201004260 | BOS          | TOR          |            13 |            12 |      9 |             243 |
| TOR199206180 | DET          | TOR          |            14 |            10 |      9 |             241 |
| BOS201504280 | TOR          | BOS          |            11 |             8 |      9 |             241 |
| DET199204080 | TOR          | DET          |            10 |             9 |      9 |             240 |
| CIN201406200 | TOR          | CIN          |            14 |             9 |      9 |             240 |
| BOS200709030 | TOR          | BOS          |            10 |            13 |      9 |             239 |
| DET198806170 | TOR          | DET          |             5 |            12 |      9 |             239 |
| TEX199209111 | TOR          | TEX          |             7 |             5 |      9 |             238 |
| ANA199805050 | TOR          | ANA          |            13 |            11 |      9 |             238 |
| TOR199108120 | BOS          | TOR          |            11 |             8 |      9 |             236 |
| NYA201809150 | TOR          | NYA          |             8 |             7 |      9 |             234 |
| BOS198806050 | TOR          | BOS          |            12 |             4 |      9 |             233 |
| NYA200806050 | TOR          | NYA          |             8 |             9 |      9 |             233 |
| DET199208060 | TOR          | DET          |            15 |            11 |      9 |             233 |
| TBA201704070 | TOR          | TBA          |             8 |            10 |      9 |             233 |
| NYA200909150 | TOR          | NYA          |            10 |             4 |      9 |             232 |
| TOR200909050 | NYA          | TOR          |             6 |             4 |      9 |             232 |
| OAK199207230 | TOR          | OAK          |             9 |             3 |      9 |             232 |
| COL201606280 | TOR          | COL          |            14 |             9 |      9 |             231 |
| TOR200004180 | ANA          | TOR          |            16 |            10 |      9 |             231 |
| MIN199808010 | TOR          | MIN          |            10 |             9 |      9 |             231 |
| BOS200707130 | TOR          | BOS          |             6 |             5 |      9 |             231 |
| TOR199807010 | NYN          | TOR          |            10 |            15 |      9 |             230 |
| TBA200204120 | TOR          | TBA          |            14 |             7 |      9 |             230 |
| TOR200109030 | NYA          | TOR          |             7 |             5 |      9 |             229 |
| PHI200906180 | TOR          | PHI          |             8 |             7 |      9 |             228 |
| DET201707140 | TOR          | DET          |             7 |             2 |      9 |             228 |
| NYA200604290 | TOR          | NYA          |             6 |            17 |      9 |             228 |
| TEX201706190 | TOR          | TEX          |             7 |             6 |      9 |             228 |
| TOR200304290 | TEX          | TOR          |            16 |            11 |      9 |             228 |
| TEX199206220 | TOR          | TEX          |            16 |             7 |      9 |             228 |
| TOR201704180 | BOS          | TOR          |             8 |             7 |      9 |             228 |
| TEX198904070 | TOR          | TEX          |            10 |             9 |      9 |             228 |
| CHA201207080 | TOR          | CHA          |            11 |             9 |      9 |             228 |
| TOR199505110 | NYA          | TOR          |            12 |            11 |      9 |             227 |
| TOR200908260 | TBA          | TOR          |             2 |             3 |      9 |             227 |
| BOS201104150 | TOR          | BOS          |             7 |             6 |      9 |             227 |
| TOR200505110 | KCA          | TOR          |             9 |            12 |      9 |             227 |
| NYA201406190 | TOR          | NYA          |             4 |             6 |      9 |             227 |
| ANA201407090 | TOR          | ANA          |             7 |             8 |      9 |             227 |
| TOR199907270 | BOS          | TOR          |            11 |             9 |      9 |             226 |
| MIL201206190 | TOR          | MIL          |            10 |             9 |      9 |             226 |
| TOR201609110 | BOS          | TOR          |            11 |             8 |      9 |             226 |
| SEA201104110 | TOR          | SEA          |             7 |             8 |      9 |             226 |
+--------------+--------------+--------------+---------------+---------------+--------+-----------------+
50 rows in set (4.420 sec)

MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', PIT_ID AS 'Pitcher', COUNT(*) AS 'Strikeouts' FROM events  WHERE PIT_ID = 'clemr001'  AND EVENT_CD = '3' GROUP BY GAME_ID ORDER BY COUNT(*) DESC LIMIT 50;
+--------------+----------+------------+
| Game         | Pitcher  | Strikeouts |
+--------------+----------+------------+
| DET199609180 | clemr001 |         20 |
| BOS198604290 | clemr001 |         20 |
| TOR199808250 | clemr001 |         18 |
| KCA198805090 | clemr001 |         16 |
| BOS198807151 | clemr001 |         16 |
| BOS199707120 | clemr001 |         16 |
| TOR199809210 | clemr001 |         15 |
| CHA198807092 | clemr001 |         15 |
| BOS198408210 | clemr001 |         15 |
| TOR199808150 | clemr001 |         15 |
| MIN199808020 | clemr001 |         14 |
| TOR199709070 | clemr001 |         14 |
| BOS198707260 | clemr001 |         14 |
| MIN199705100 | clemr001 |         14 |
| TEX198807250 | clemr001 |         14 |
| BOS199605010 | clemr001 |         13 |
| BAL199305110 | clemr001 |         13 |
| NYA199906170 | clemr001 |         13 |
| NYA200005280 | clemr001 |         13 |
| NYA200205190 | clemr001 |         13 |
| BOS198804140 | clemr001 |         13 |
| NYA198709300 | clemr001 |         13 |
| BOS198908310 | clemr001 |         13 |
| NYA200206030 | clemr001 |         13 |
| TOR199708120 | clemr001 |         13 |
| BOS198807300 | clemr001 |         13 |
| TOR199706160 | clemr001 |         12 |
| DET199406070 | clemr001 |         12 |
| BOS198709090 | clemr001 |         12 |
| CLE198706170 | clemr001 |         12 |
| NYA199705210 | clemr001 |         12 |
| CHA198906160 | clemr001 |         12 |
| MIL200409240 | clemr001 |         12 |
| CLE199204122 | clemr001 |         12 |
| BOS198710040 | clemr001 |         12 |
| BOS199305280 | clemr001 |         11 |
| DET199809160 | clemr001 |         11 |
| CLE199006030 | clemr001 |         11 |
| BOS198804040 | clemr001 |         11 |
| BOS199204170 | clemr001 |         11 |
| CLE199708170 | clemr001 |         11 |
| BOS198608300 | clemr001 |         11 |
| DET198804190 | clemr001 |         11 |
| TOR199809260 | clemr001 |         11 |
| HOU200405110 | clemr001 |         11 |
| OAK199008140 | clemr001 |         11 |
| BOS199104130 | clemr001 |         11 |
| BOS199604260 | clemr001 |         11 |
| NYA200007190 | clemr001 |         11 |
| TOR199809050 | clemr001 |         11 |
+--------------+----------+------------+
50 rows in set (15 min 44.284 sec)

MariaDB [retrosheet]> help source;

Nothing found
Please try to run 'help contents' for a list of all accessible topics

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

MariaDB [retrosheet]> SHOW TABLES;
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
| subs                        |
+-----------------------------+
23 rows in set (0.004 sec)

MariaDB [retrosheet]> DESCRIBE lkup_id_person;
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
7 rows in set (0.003 sec)

MariaDB [retrosheet]> source /newdata/dev/git/Python/Chadwick/sql/retrosheet_rosters-table_schema.sql
Query OK, 0 rows affected, 1 warning (0.001 sec)

Query OK, 0 rows affected (1.895 sec)

MariaDB [retrosheet]> SHOW TABLES;
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

MariaDB [retrosheet]> describe rosters;
+---------------+-------------+------+-----+---------+-------+
| Field         | Type        | Null | Key | Default | Extra |
+---------------+-------------+------+-----+---------+-------+
| PLAYER_ID     | varchar(8)  | NO   | MUL | NULL    |       |
| LAST_NAME     | varchar(24) | NO   |     | NULL    |       |
| FIRST_NAME    | varchar(16) | YES  |     | ?       |       |
| BAT_HAND_CD   | char(1)     | NO   |     | NULL    |       |
| THROW_HAND_CD | char(1)     | NO   |     | NULL    |       |
| TEAM_ID       | char(3)     | NO   |     | NULL    |       |
| POS_ID        | char(8)     | NO   |     | NULL    |       |
+---------------+-------------+------+-----+---------+-------+
7 rows in set (0.003 sec)

MariaDB [retrosheet]> source /newdata/dev/git/Python/Chadwick/sql/rosters.sql
Query OK, 53 rows affected, 6 warnings (0.591 sec)   
Records: 53  Deleted: 0  Skipped: 0  Warnings: 6

MariaDB [retrosheet]> SELECT * FROM rosters;
+-----------+-------------+------------+-------------+---------------+---------+--------+
| PLAYER_ID | LAST_NAME   | FIRST_NAME | BAT_HAND_CD | THROW_HAND_CD | TEAM_ID | POS_ID |
+-----------+-------------+------------+-------------+---------------+---------+--------+
     |a001  | Albers      | Andrew     | R           | L             | TOR     | P
    |nd001  | Barney      | Darwin     | R           | R             | TOR     | 2B
    |tj002  | Bautista    | Jose       | R           | R             | TOR     | OF
     |m001  | Boyd        | Matt       | L           | L             | TOR     | P
     |m001  | Buehrle     | Mark       | L           | L             | TOR     | P
    |re001  | Carrera     | Ezequiel   | L           | L             | TOR     | OF
     |m002  | Castro      | Miguel     | R           | R             | TOR     | P
     |b001  | Cecil       | Brett      | R           | L             | TOR     | P
     |p001  | Coke        | Phil       | L           | L             | TOR     | P
    |ac001  | Colabello   | Chris      | R           | R             | TOR     | OF
     |s001  | Copeland    | Scott      | R           | R             | TOR     | P
     |s001  | Delabar     | Steve      | R           | R             | TOR     | P
    |zj004  | Diaz        | Jonathan   | R           | R             | TOR     | SS
     |r001  | Dickey      | R.A.       | R           | R             | TOR     | P
    |aj001  | Donaldson   | Josh       | R           | R             | TOR     | 3B
     |f001  | Doubront    | Felix      | L           | L             | TOR     | P
    |ae001  | Encarnacion | Edwin      | R           | R             | TOR     | DH
     |m001  | Estrada     | Marco      | R           | R             | TOR     | P
     |j003  | Francis     | Jeff       | L           | L             | TOR     | P
    |nr001  | Goins       | Ryan       | L           | R             | TOR     | 2B
    |um001  | Hague       | Matt       | R           | R             | TOR     | 1B
     |l001  | Hawkins     | LaTroy     | R           | R             | TOR     | P
     |l001  | Hendriks    | Liam       | R           | R             | TOR     | P
     |d001  | Hutchison   | Drew       | L           | R             | TOR     | P
     |c001  | Hynes       | Colt       | L           | L             | TOR     | P
     |c001  | Jenkins     | Chad       | R           | R             | TOR     | P
    |am001  | Kawasaki    | Munenori   | L           | R             | TOR     | 2B
     |a001  | Loup        | Aaron      | L           | L             | TOR     | P
     |m002  | Lowe        | Mark       | L           | R             | TOR     | P
     |r004  | Martin      | Russell    | R           | R             | TOR     | C
     |d001  | Navarro     | Dioner     | B           | R             | TOR     | C
     |d002  | Norris      | Daniel     | L           | L             | TOR     | P
     |r001  | Osuna       | Roberto    | R           | R             | TOR     | P
    |nc001  | Pennington  | Cliff      | B           | R             | TOR     | 2B
    |lk001  | Pillar      | Kevin      | R           | R             | TOR     | OF
    |pd001  | Pompey      | Dalton     | B           | R             | TOR     | OF
     |d001  | Price       | David      | L           | L             | TOR     | P
     |r001  | Rasmussen   | Rob        | R           | L             | TOR     | P
     |t002  | Redmond     | Todd       | R           | R             | TOR     | P
    |eb001  | Revere      | Ben        | L           | R             | TOR     | OF
    |ej001  | Reyes       | Jose       | B           | R             | TOR     | SS
     |a006  | Sanchez     | Aaron      | R           | R             | TOR     | P
    |nm001  | Saunders    | Michael    | L           | R             | TOR     | OF
     |b001  | Schultz     | Bo         | R           | R             | TOR     | P
    |aj001  | Smoak       | Justin     | B           | L             | TOR     | 1B
     |m001  | Stroman     | Marcus     | R           | R             | TOR     | P
     |r001  | Tepera      | Ryan       | R           | R             | TOR     | P
     |j001  | Thole       | Josh       | L           | R             | TOR     | C
    |ls001  | Tolleson    | Steven     | R           | R             | TOR     | 2B
    |vd001  | Travis      | Devon      | R           | R             | TOR     | 2B
    |ot001  | Tulowitzki  | Troy       | R           | R             | TOR     | SS
    |ed001  | Valencia    | Danny      | R           | R             | TOR     | OF
| �         |             |            |             |               |         |        |
+-----------+-------------+------------+-------------+---------------+---------+--------+
53 rows in set (0.001 sec)

MariaDB [retrosheet]> SELECT * FROM subs WHERE PERSON_ID = 'cartj001';
ERROR 1054 (42S22): Unknown column 'PERSON_ID' in 'where clause'
MariaDB [retrosheet]> describe subs;
+----------------+-------------+------+-----+---------+-------+
| Field          | Type        | Null | Key | Default | Extra |
+----------------+-------------+------+-----+---------+-------+
| GAME_ID        | varchar(12) | YES  | MUL | NULL    |       |
| INN_CT         | int(11)     | YES  |     | NULL    |       |
| BAT_HOME_ID    | int(11)     | YES  |     | NULL    |       |
| SUB_ID         | varchar(8)  | YES  |     | NULL    |       |
| SUB_HOME_ID    | int(11)     | YES  |     | NULL    |       |
| SUB_LINEUP_ID  | int(11)     | YES  |     | NULL    |       |
| SUB_FLD_CD     | int(11)     | YES  |     | NULL    |       |
| REMOVED_ID     | varchar(8)  | YES  |     | NULL    |       |
| REMOVED_FLD_CD | int(11)     | YES  |     | NULL    |       |
| EVENT_ID       | int(11)     | YES  |     | NULL    |       |
+----------------+-------------+------+-----+---------+-------+
10 rows in set (0.002 sec)

MariaDB [retrosheet]> SELECT * FROM lkup_id_person  WHERE PERSON_ID = 'cartj001';
+-----------+-----------+------------+--------------+------------+-------------+------------+
| PERSON_ID | LAST_NAME | FIRST_NAME | PLAYER_DEBUT | MGR_DEBUT  | COACH_DEBUT | UMP_DEBUT  |
+-----------+-----------+------------+--------------+------------+-------------+------------+
| cartj001  | Carter    | Joe        | 1983-07-30   | 0000-00-00 | 0000-00-00  | 0000-00-00 |
+-----------+-----------+------------+--------------+------------+-------------+------------+
1 row in set (0.023 sec)

MariaDB [retrosheet]> SELECT * FROM lkup_id_person  WHERE PERSON_ID = 'aaroh101';
+-----------+-----------+------------+--------------+------------+-------------+------------+
| PERSON_ID | LAST_NAME | FIRST_NAME | PLAYER_DEBUT | MGR_DEBUT  | COACH_DEBUT | UMP_DEBUT  |
+-----------+-----------+------------+--------------+------------+-------------+------------+
| aaroh101  | Aaron     | Hank       | 1954-04-13   | 0000-00-00 | 0000-00-00  | 0000-00-00 |
+-----------+-----------+------------+--------------+------------+-------------+------------+
1 row in set (0.021 sec)

MariaDB [retrosheet]> SELECT * FROM lkup_id_person  WHERE PERSON_ID = 'bondb%01';
Empty set (0.022 sec)

MariaDB [retrosheet]> SELECT * FROM lkup_id_person  WHERE PERSON_ID = 'bondb*01';
Empty set (0.000 sec)

MariaDB [retrosheet]> SELECT * FROM lkup_id_person  WHERE PERSON_ID = 'bondb#01';
Empty set (0.001 sec)

MariaDB [retrosheet]> SELECT * FROM lkup_id_person  WHERE PERSON_ID LIKE 'bondb_01';
+-----------+-----------+------------+--------------+------------+-------------+------------+
| PERSON_ID | LAST_NAME | FIRST_NAME | PLAYER_DEBUT | MGR_DEBUT  | COACH_DEBUT | UMP_DEBUT  |
+-----------+-----------+------------+--------------+------------+-------------+------------+
| bondb001  | Bonds     | Barry      | 1986-05-30   | 0000-00-00 | 2016-04-05  | 0000-00-00 |
| bondb101  | Bonds     | Bobby      | 1968-06-25   | 0000-00-00 | 1984-04-03  | 0000-00-00 |
+-----------+-----------+------------+--------------+------------+-------------+------------+
2 rows in set (0.048 sec)

MariaDB [retrosheet]> SELECT * FROM lkup_id_person  WHERE PERSON_ID LIKE 'acunr%';
+-----------+-----------+------------+--------------+------------+-------------+------------+
| PERSON_ID | LAST_NAME | FIRST_NAME | PLAYER_DEBUT | MGR_DEBUT  | COACH_DEBUT | UMP_DEBUT  |
+-----------+-----------+------------+--------------+------------+-------------+------------+
| acunr001  | Acuna     | Ronald     | 2018-04-25   | 0000-00-00 | 0000-00-00  | 0000-00-00 |
+-----------+-----------+------------+--------------+------------+-------------+------------+
1 row in set (0.001 sec)

MariaDB [retrosheet]> SELECT * FROM lkup_id_person  WHERE PERSON_ID LIKE 'alonp%';
Empty set (0.001 sec)

MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', BAT_ID AS 'Batter', COUNT(*) AS 'RBIs' 
    -> FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT >= 1
    -> GROUP BY GAME_ID ORDER BY COUNT(*) DESC;
+--------------+----------+------+
| Game         | Batter   | RBIs |
+--------------+----------+------+
| BRO195607300 | aaroh101 |    3 |
| MLN195607221 | aaroh101 |    2 |
| PHI195609131 | aaroh101 |    2 |
| CHN195605310 | aaroh101 |    2 |
| MLN195609031 | aaroh101 |    2 |
| PHI195609132 | aaroh101 |    2 |
| CHN195609091 | aaroh101 |    2 |
| NY1195607260 | aaroh101 |    2 |
| CHN195605301 | aaroh101 |    2 |
| SLN195605280 | aaroh101 |    2 |
| MLN195604170 | aaroh101 |    2 |
| MLN195607200 | aaroh101 |    2 |
| CHN195605302 | aaroh101 |    2 |
| MLN195605070 | aaroh101 |    1 |
| MLN195608230 | aaroh101 |    1 |
| PIT195606210 | aaroh101 |    1 |
| CIN195608190 | aaroh101 |    1 |
| CIN195605131 | aaroh101 |    1 |
| MLN195607160 | aaroh101 |    1 |
| PHI195606250 | aaroh101 |    1 |
| MLN195607042 | aaroh101 |    1 |
| NY1195605170 | aaroh101 |    1 |
| MLN195606120 | aaroh101 |    1 |
| MLN195606020 | aaroh101 |    1 |
| MLN195608260 | aaroh101 |    1 |
| SLN195604222 | aaroh101 |    1 |
| CIN195609250 | aaroh101 |    1 |
| MLN195608081 | aaroh101 |    1 |
| CIN195605132 | aaroh101 |    1 |
| MLN195607190 | aaroh101 |    1 |
| PHI195606260 | aaroh101 |    1 |
| MLN195607131 | aaroh101 |    1 |
| MLN195606140 | aaroh101 |    1 |
| MLN195609032 | aaroh101 |    1 |
| BRO195605220 | aaroh101 |    1 |
| MLN195606060 | aaroh101 |    1 |
| MLN195609010 | aaroh101 |    1 |
| MLN195608212 | aaroh101 |    1 |
| PHI195609150 | aaroh101 |    1 |
| CIN195607030 | aaroh101 |    1 |
| PHI195606270 | aaroh101 |    1 |
| CHN195609092 | aaroh101 |    1 |
| MLN195607140 | aaroh101 |    1 |
| PHI195605160 | aaroh101 |    1 |
| MLN195607041 | aaroh101 |    1 |
| MLN195609230 | aaroh101 |    1 |
| BRO195606171 | aaroh101 |    1 |
| MLN195606090 | aaroh101 |    1 |
| MLN195609020 | aaroh101 |    1 |
| SLN195609280 | aaroh101 |    1 |
+--------------+----------+------+
50 rows in set (16 min 36.377 sec)

MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', BAT_ID AS 'Batter', COUNT(RBI_CT) AS 'RBIs'  FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT >= 1 GROUP BY GAME_ID ORDER BY GAME_ID DESC;
^CCtrl-C -- query killed. Continuing normally.
ERROR 1317 (70100): Query execution was interrupted
MariaDB [retrosheet]> SELECT GAME_ID AS 'Game', BAT_ID AS 'Batter', SUM(RBI_CT) AS 'RBIs'  FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT >= 1 GROUP BY GAME_ID ORDER BY GAME_ID DESC;
+--------------+----------+------+
| Game         | Batter   | RBIs |
+--------------+----------+------+
| SLN195609280 | aaroh101 |    1 |
| SLN195605280 | aaroh101 |    2 |
| SLN195604222 | aaroh101 |    1 |
| PIT195606210 | aaroh101 |    1 |
| PHI195609150 | aaroh101 |    3 |
| PHI195609132 | aaroh101 |    2 |
| PHI195609131 | aaroh101 |    2 |
| PHI195606270 | aaroh101 |    1 |
| PHI195606260 | aaroh101 |    1 |
| PHI195606250 | aaroh101 |    1 |
| PHI195605160 | aaroh101 |    1 |
| NY1195607260 | aaroh101 |    4 |
| NY1195605170 | aaroh101 |    2 |
| MLN195609230 | aaroh101 |    1 |
| MLN195609032 | aaroh101 |    1 |
| MLN195609031 | aaroh101 |    2 |
| MLN195609020 | aaroh101 |    1 |
| MLN195609010 | aaroh101 |    1 |
| MLN195608260 | aaroh101 |    2 |
| MLN195608230 | aaroh101 |    1 |
| MLN195608212 | aaroh101 |    1 |
| MLN195608081 | aaroh101 |    1 |
| MLN195607221 | aaroh101 |    2 |
| MLN195607200 | aaroh101 |    4 |
| MLN195607190 | aaroh101 |    1 |
| MLN195607160 | aaroh101 |    1 |
| MLN195607140 | aaroh101 |    1 |
| MLN195607131 | aaroh101 |    1 |
| MLN195607042 | aaroh101 |    3 |
| MLN195607041 | aaroh101 |    1 |
| MLN195606140 | aaroh101 |    1 |
| MLN195606120 | aaroh101 |    1 |
| MLN195606090 | aaroh101 |    1 |
| MLN195606060 | aaroh101 |    2 |
| MLN195606020 | aaroh101 |    1 |
| MLN195605070 | aaroh101 |    1 |
| MLN195604170 | aaroh101 |    2 |
| CIN195609250 | aaroh101 |    1 |
| CIN195608190 | aaroh101 |    2 |
| CIN195607030 | aaroh101 |    1 |
| CIN195605132 | aaroh101 |    1 |
| CIN195605131 | aaroh101 |    2 |
| CHN195609092 | aaroh101 |    1 |
| CHN195609091 | aaroh101 |    2 |
| CHN195605310 | aaroh101 |    2 |
| CHN195605302 | aaroh101 |    3 |
| CHN195605301 | aaroh101 |    2 |
| BRO195607300 | aaroh101 |    4 |
| BRO195606171 | aaroh101 |    1 |
| BRO195605220 | aaroh101 |    1 |
+--------------+----------+------+
50 rows in set (17 min 36.968 sec)

MariaDB [retrosheet]> SELECT SUM(RBI_CT) AS 'RBIs' FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT >= 1 GROUP BY YEAR_ID;
+------+
| RBIs |
+------+
|   79 |
+------+
1 row in set (2 min 9.626 sec)

MariaDB [retrosheet]> SELECT SUM(RBI_CT) AS 'H Aaron RBIs in 1956' FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT >= 1 GROUP BY YEAR_ID;
+----------------------+
| H Aaron RBIs in 1956 |
+----------------------+
|                   79 |
+----------------------+
1 row in set (1 min 42.660 sec)

MariaDB [retrosheet]> exit
Bye
/newdata/dev/git/Python/Chadwick/sql | Fri Jan 29 22:09:51 | marksa@Ares-A717-72G | bash 5.0.17 | (master)
2001 >