
-- http://basql.wikidot.com/house-linear-weights
-- My method of figuring empiric linear weights using Retrosheet data. 
-- In this case, the linear weights are meant to be used with official batting totals 
-- - to that end, ROE are treated as an out, and SB/CS linear weights are calculated by including events 
-- that occur during another event code, like a walk, strikeout, etc.

CREATE TABLE BASES_CD AS
SELECT DISTINCT START_BASES_CD
    , IF(RUN1_ORIGIN_EVENT_ID > 0,1,0) AS RUN1
    , IF(RUN2_ORIGIN_EVENT_ID > 0,1,0) AS RUN2
    , IF(RUN3_ORIGIN_EVENT_ID > 0,1,0) AS RUN3
FROM retrosheet.events
WHERE YEAR_ID = 2008
ORDER BY START_BASES_CD;


CREATE TABLE complete_innings 
AS SELECT YEAR_ID, GAME_ID, INN_CT, BAT_HOME_ID
FROM retrosheet.events e
WHERE INN_END_FL = "T"
AND EVENT_OUTS_CT + OUTS_CT = 3
AND IF(INN_CT = 9 AND BAT_HOME_ID = 1,1,0)=0;

CREATE INDEX complete_innings_idx ON complete_innings(GAME_ID,INN_CT,BAT_HOME_ID);


CREATE TABLE fate_runs_complete AS
SELECT e.YEAR_ID
    , OUTS_CT+EVENT_OUTS_CT AS OUTS
    , AVG(INN_PA_CT)
    , AVG(FATE_RUNS_CT + EVENT_RUNS_CT - IF(RUN3_FATE_ID>3,1,0) - IF(RUN2_FATE_ID>3,1,0)
     - IF(RUN1_FATE_ID>3,1,0) - IF(BAT_FATE_ID>3,1,0)) AS FATE_RE
FROM retrosheet.events e, lwts.complete_innings c
WHERE e.GAME_ID = c.GAME_ID
AND e.INN_CT = c.INN_CT
AND e.BAT_HOME_ID = c.BAT_HOME_ID
AND BAT_EVENT_FL = "T"
AND PA_TRUNC_FL = "F"
AND EVENT_CD != 23
GROUP BY YEAR_ID, OUTS;


CREATE TABLE batter_runner_runs_complete AS
SELECT    e.YEAR_ID
    , OUTS_CT
    , AVG(IF(BAT_FATE_ID>3,1,0)) AS BAT_RE
    , SUM(IF(RUN1_FATE_ID>3,1,0))/SUM(IF(RUN1_ORIGIN_EVENT_ID > 0,1,0)) AS RUN1_RE
    , AVG(IF(RUN1_ORIGIN_EVENT_ID > 0,1,0)) AS RUN1_NUM
    , SUM(IF(RUN2_FATE_ID>3,1,0))/SUM(IF(RUN2_ORIGIN_EVENT_ID > 0,1,0)) AS RUN2_RE
    , AVG(IF(RUN2_ORIGIN_EVENT_ID > 0,1,0)) AS RUN2_NUM    
    , SUM(IF(RUN3_FATE_ID>3,1,0))/SUM(IF(RUN3_ORIGIN_EVENT_ID > 0,1,0)) AS RUN3_RE
    , AVG(IF(RUN3_ORIGIN_EVENT_ID > 0,1,0)) AS RUN3_NUM
FROM retrosheet.events e, lwts.complete_innings c
WHERE e.GAME_ID = c.GAME_ID
AND e.INN_CT = c.INN_CT
AND e.BAT_HOME_ID = c.BAT_HOME_ID
AND BAT_EVENT_FL = "T"
AND PA_TRUNC_FL = "F"
GROUP BY YEAR_ID, OUTS_CT;


CREATE TABLE inning_runs_complete AS
SELECT e.YEAR_ID, SUM(EVENT_RUNS_CT)/SUM(IF(INN_NEW_FL = "T",1,0)) AS INN_RUNS
FROM retrosheet.events e, lwts.complete_innings c
WHERE e.GAME_ID = c.GAME_ID
AND e.INN_CT = c.INN_CT
AND e.BAT_HOME_ID = c.BAT_HOME_ID
GROUP BY YEAR_ID;


CREATE TABLE re_temp_complete AS
SELECT r.YEAR_ID
    , r.OUTS_CT
    , START_BASES_CD AS BASES_CD
    , (RUN1_RE*RUN1)+(RUN2_RE*RUN2)+(RUN3_RE*RUN3)+IF(r.OUTS_CT=0,INN_RUNS,FATE_RE) AS RE
FROM bases_cd b, batter_runner_runs_complete r, fate_runs_complete f, inning_runs_complete i
WHERE r.YEAR_ID = f.YEAR_ID
AND r.OUTS_CT = f.OUTS
AND r.YEAR_ID = i.YEAR_ID;


CREATE TABLE re_complete AS
SELECT * FROM (SELECT * FROM re_temp_complete
UNION ALL
SELECT DISTINCT
YEAR_ID
    , 3 AS OUTS_CT
    , BASES_CD
    , 0 AS RE
FROM re_temp_complete) a
ORDER BY YEAR_ID, OUTS_CT, BASES_CD;

CREATE INDEX re_complete_idx
ON re_complete (YEAR_ID,OUTS_CT,BASES_CD);


CREATE TABLE errors_year AS
SELECT e.YEAR_ID, SUM(EVENT_RUNS_CT+r2.RE-r1.RE) AS Err, COUNT(1) AS Num
FROM retrosheet.events e, re_complete r1, re_complete r2, lwts.complete_innings c
WHERE e.GAME_ID = c.GAME_ID
AND e.INN_CT = c.INN_CT
AND e.BAT_HOME_ID = c.BAT_HOME_ID
AND e.YEAR_ID = r1.YEAR_ID
AND e.START_BASES_CD = r1.BASES_CD
AND e.OUTS_CT = r1.OUTS_CT
AND e.YEAR_ID = r2.YEAR_ID
AND e.END_BASES_CD = r2.BASES_CD
AND e.OUTS_CT + EVENT_OUTS_CT = r2.OUTS_CT
GROUP BY e.YEAR_ID;


CREATE TABLE walk_state AS
SELECT a.START_BASES_CD, a.END_BASES_CD, a.EVENT_RUNS_CT
FROM (SELECT START_BASES_CD, END_BASES_CD, EVENT_RUNS_CT, COUNT(1) AS Num
FROM retrosheet.events e
WHERE YEAR_ID = 2008
AND EVENT_CD = 14
GROUP BY START_BASES_CD, END_BASES_CD, EVENT_RUNS_CT) a, (SELECT START_BASES_CD, MAX(Num) AS Num
FROM (SELECT START_BASES_CD, END_BASES_CD, EVENT_RUNS_CT, COUNT(1) AS Num
FROM retrosheet.events e
WHERE YEAR_ID = 2008
AND EVENT_CD = 14
GROUP BY START_BASES_CD, END_BASES_CD, EVENT_RUNS_CT) a
GROUP BY START_BASES_CD) b
WHERE a.START_BASES_CD = b.START_BASES_CD
AND a.Num = b.Num;


CREATE TABLE batter_lwts_official AS
SELECT e.YEAR_ID
    , (CASE WHEN e.EVENT_CD BETWEEN 18 AND 19 THEN 2 ELSE e.EVENT_CD END) AS EVENT
    , COUNT(1) AS Num
    , AVG(CASE WHEN e.EVENT_CD = 3 THEN 1
               WHEN e.EVENT_CD BETWEEN 14 AND 16 THEN 0
               ELSE e.EVENT_OUTS_CT END) AS Outs
    , AVG(CASE WHEN e.EVENT_CD = 3 THEN r2.RE-r1.RE
               WHEN e.EVENT_CD BETWEEN 14 AND 16 THEN w.EVENT_RUNS_CT+r2.RE-r1.RE
               ELSE e.EVENT_RUNS_CT+r2.RE-r1.RE END) AS LWTS 
FROM retrosheet.events e, re_complete r1, re_complete r2
    , lwts.complete_innings c, walk_state w
WHERE e.BAT_EVENT_FL = "T"
AND e.EVENT_CD != 17
AND e.START_BASES_CD = w.START_BASES_CD
AND e.GAME_ID = c.GAME_ID
AND e.INN_CT = c.INN_CT
AND e.BAT_HOME_ID = c.BAT_HOME_ID
AND e.YEAR_ID = r1.YEAR_ID
AND e.START_BASES_CD = r1.BASES_CD
AND e.OUTS_CT = r1.OUTS_CT
AND e.YEAR_ID = r2.YEAR_ID
AND (CASE WHEN EVENT_CD = 3 THEN e.START_BASES_CD
          WHEN EVENT_CD BETWEEN 14 AND 16 THEN w.END_BASES_CD 
          ELSE e.END_BASES_CD END) = r2.BASES_CD
AND (CASE WHEN EVENT_CD = 3 THEN e.OUTS_CT + 1
          WHEN EVENT_CD BETWEEN 14 AND 16 THEN e.OUTS_CT
          ELSE e.OUTS_CT + e.EVENT_OUTS_CT END) = r2.OUTS_CT
GROUP BY e.YEAR_ID, EVENT;


CREATE TABLE runs_pa_complete AS
SELECT e.YEAR_ID
    , SUM(EVENT_RUNS_CT) / SUM(IF(BAT_EVENT_FL = "T" AND e.EVENT_CD != 17,1,0)) AS R_PA
    , SUM(EVENT_RUNS_CT) / SUM(CASE WHEN e.EVENT_CD = 3 THEN 1
                                    WHEN e.EVENT_CD BETWEEN 14 AND 16 THEN 0
                                    ELSE e.EVENT_OUTS_CT END) AS R_Out
FROM retrosheet.events e, lwts.complete_innings c
WHERE e.GAME_ID = c.GAME_ID
AND e.INN_CT = c.INN_CT
AND e.BAT_HOME_ID = c.BAT_HOME_ID
GROUP BY YEAR_ID;


CREATE TABLE runner_lwts_official AS
SELECT e.YEAR_ID
    , "4" AS EVENT
    , SUM(IF(RUN1_SB_FL ="T",1,0)+IF(RUN2_SB_FL ="T",1,0)+IF(RUN3_SB_FL ="T",1,0)) AS Num
    , SUM(CASE WHEN e.EVENT_CD = 3 THEN IF(e.EVENT_OUTS_CT>0,e.EVENT_OUTS_CT-1,0) ELSE e.EVENT_OUTS_CT END)
        / SUM(IF(RUN1_SB_FL ="T",1,0)+IF(RUN2_SB_FL ="T",1,0)+IF(RUN3_SB_FL ="T",1,0)) AS Outs
    , SUM(e.EVENT_RUNS_CT-w.EVENT_RUNS_CT+r2.RE-r1.RE)
        / SUM(IF(RUN1_SB_FL ="T",1,0)+IF(RUN2_SB_FL ="T",1,0)+IF(RUN3_SB_FL ="T",1,0)) AS LWTS 
FROM retrosheet.events e, re_complete r1, re_complete r2
    , lwts.complete_innings c, walk_state w
WHERE (RUN1_SB_FL ="T" OR RUN2_SB_FL ="T" OR RUN3_SB_FL ="T")
AND e.START_BASES_CD = w.START_BASES_CD
AND e.GAME_ID = c.GAME_ID
AND e.INN_CT = c.INN_CT
AND e.BAT_HOME_ID = c.BAT_HOME_ID
AND e.YEAR_ID = r1.YEAR_ID
AND (CASE WHEN EVENT_CD = 3 THEN e.START_BASES_CD
          WHEN EVENT_CD BETWEEN 14 AND 16 THEN w.END_BASES_CD 
          ELSE e.START_BASES_CD END) = r1.BASES_CD
AND (CASE WHEN EVENT_CD = 3 THEN e.OUTS_CT + 1
          ELSE e.OUTS_CT END) = r1.OUTS_CT
AND e.YEAR_ID = r2.YEAR_ID
AND e.END_BASES_CD = r2.BASES_CD
AND e.OUTS_CT + e.EVENT_OUTS_CT = r2.OUTS_CT
GROUP BY e.YEAR_ID
UNION ALL
SELECT e.YEAR_ID
    , "6" AS EVENT
    , SUM(IF(RUN1_CS_FL ="T",1,0)+IF(RUN2_CS_FL ="T",1,0)+IF(RUN3_CS_FL ="T",1,0)) AS Num
    , SUM(CASE WHEN e.EVENT_CD = 3 THEN IF(e.EVENT_OUTS_CT>0,e.EVENT_OUTS_CT-1,0) ELSE e.EVENT_OUTS_CT END)
        / SUM(IF(RUN1_CS_FL ="T",1,0)+IF(RUN2_CS_FL ="T",1,0)+IF(RUN3_CS_FL ="T",1,0)) AS Outs
    , SUM(IF(e.EVENT_RUNS_CT>0,e.EVENT_RUNS_CT-w.EVENT_RUNS_CT,0)+r2.RE-r1.RE)
        / SUM(IF(RUN1_CS_FL ="T",1,0)+IF(RUN2_CS_FL ="T",1,0)+IF(RUN3_CS_FL ="T",1,0)) AS LWTS 
FROM retrosheet.events e, re_complete r1, re_complete r2, lwts.complete_innings c, walk_state w
WHERE (RUN1_CS_FL ="T" OR RUN2_CS_FL ="T" OR RUN3_CS_FL ="T")
AND e.START_BASES_CD = w.START_BASES_CD
AND e.GAME_ID = c.GAME_ID
AND e.INN_CT = c.INN_CT
AND e.BAT_HOME_ID = c.BAT_HOME_ID
AND e.YEAR_ID = r1.YEAR_ID
AND (CASE WHEN EVENT_CD = 3 THEN e.START_BASES_CD
          WHEN EVENT_CD BETWEEN 14 AND 16 THEN w.END_BASES_CD 
          ELSE e.START_BASES_CD END) = r1.BASES_CD
AND (CASE WHEN EVENT_CD = 3 THEN e.OUTS_CT + 1 ELSE e.OUTS_CT END) = r1.OUTS_CT
AND e.YEAR_ID = r2.YEAR_ID
AND e.END_BASES_CD = r2.BASES_CD
AND e.OUTS_CT + e.EVENT_OUTS_CT = r2.OUTS_CT
GROUP BY e.YEAR_ID;
