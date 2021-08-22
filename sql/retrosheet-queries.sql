
-- 2021-08-20

-- top 30 RBI players of 1956
SELECT BAT_ID AS 'Batter', SUM(RBI_CT) AS 'RBIs' FROM events WHERE YEAR_ID = '1956' GROUP BY BAT_ID ORDER BY SUM(RBI_CT) DESC LIMIT 30;

-- H Aaron yearly RBI totals
SELECT YEAR_ID AS 'Year', SUM(RBI_CT) AS 'RBIs' FROM events WHERE BAT_ID = 'aaroh101' GROUP BY YEAR_ID ORDER BY YEAR_ID ASC;

-- ======================================================================================================

-- 2021-08-19

-- all multi-RBI games of H Aaron in 1956, by num RBIs
SELECT GAME_ID AS 'Game', BAT_ID AS 'Batter', SUM(RBI_CT) AS 'RBIs' 
FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT > 1 
GROUP BY GAME_ID ORDER BY SUM(RBI_CT) DESC;

-- 30 top strikeout games of Sandy Koufax in DESC order
SELECT GAME_ID AS 'Game', COUNT(*) AS 'Strikeouts' 
FROM events WHERE PIT_ID = 'koufs101' AND EVENT_CD = '3' 
GROUP BY GAME_ID ORDER BY COUNT(*) DESC LIMIT 30;

-- ======================================================================================================

-- longest 9-inning games by clock time: all that were at least 250 minutes
SELECT GAME_ID, AWAY_TEAM_ID, HOME_TEAM_ID, AWAY_SCORE_CT, HOME_SCORE_CT, INN_CT, MINUTES_GAME_CT 
FROM games  WHERE INN_CT = 9 AND MINUTES_GAME_CT >= 250 
ORDER BY MINUTES_GAME_CT DESC;

-- 50 longest 9-inning Blue Jay games by minutes
SELECT GAME_ID, AWAY_TEAM_ID, HOME_TEAM_ID, AWAY_SCORE_CT, HOME_SCORE_CT, INN_CT, MINUTES_GAME_CT 
FROM games WHERE INN_CT = 9 AND ( HOME_TEAM_ID = 'TOR' OR AWAY_TEAM_ID = 'TOR' ) 
ORDER BY MINUTES_GAME_CT DESC LIMIT 50;

-- 50 top strikeout games of Roger Clemens in order
SELECT GAME_ID AS 'Game', PIT_ID AS 'Pitcher', COUNT(*) AS 'Strikeouts' 
FROM events WHERE PIT_ID = 'clemr001' AND EVENT_CD = '3'
GROUP BY GAME_ID ORDER BY COUNT(*) DESC LIMIT 50;

-- all RBIs of H Aaron in 1956, by game id
SELECT GAME_ID AS 'Game', BAT_ID AS 'Batter', SUM(RBI_CT) AS 'RBIs' 
FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT >= 1 
GROUP BY GAME_ID ORDER BY GAME_ID ASC;

-- sum of RBIs by H Aaron in 1956
SELECT SUM(RBI_CT) AS 'H Aaron RBIs in 1956' 
FROM events WHERE YEAR_ID = '1956' AND BAT_ID = 'aaroh101' AND RBI_CT >= 1 
GROUP BY YEAR_ID;
