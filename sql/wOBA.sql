CREATE TABLE PrimPos AS
SELECT playerID
, yearID
, teamID
, MAX(G) AS G
, POS
FROM (SELECT * from bdb.fielding
WHERE IF(yearID>1995 AND POS = "OF",1,0) != 1 ORDER BY G Desc) f
GROUP BY playerID, yearID, teamID;


CREATE VIEW LeagueRunsPerOut
AS SELECT p.yearID 
, Sum(p.R)/Sum(p.IPouts) AS RperOut 
, Sum(p.R) AS totR 
, Sum(p.IPouts) AS totOuts
FROM 
PrimPos 
INNER JOIN 
bdb.pitching p
ON PrimPos.yearID = p.yearID 
AND PrimPos.playerID = p.playerID
WHERE PrimPos.POS="P"
GROUP BY p.yearID;


CREATE TABLE RunValues
AS SELECT yearID 
, RperOut 
, @rb := RperOut+0.14 AS runBB 
, @rb+0.025 AS runHB 
, @rs := @rb+0.155 AS run1B 
, @rd := @rs+0.3 AS run2B 
, @rd+0.27 AS run3B 
, 1.4 AS runHR 
, 0.2 AS runSB 
, 2*RperOut+0.075 AS runCS 
FROM LeagueRunsPerOut;


CREATE TABLE RunValues1A AS
SELECT r.yearID 
, r.RperOut 
, r.runBB 
, r.runHB 
, r.run1B 
, r.run2B 
, r.run3B 
, r.runHR 
, r.runSB 
, r.runCS 
, SUM(runBB*(BB-COALESCE(IBB,0))+runHB*COALESCE(HBP,0)+run1B*(H-2B-3b-HR)+run2B*2B+run3B*3B+1.4*HR+runSB*COALESCE(SB,0) - runCS*COALESCE(CS,0))/SUM(AB-H+COALESCE(SF,0)) AS runMinus 
, SUM(runBB*(BB-COALESCE(IBB,0))+runHB*COALESCE(HBP,0)+run1B*(H-2b-3b-HR)+run2B*2B+run3B*3B+1.4*HR+runSB*COALESCE(SB,0) - runCS*COALESCE(CS,0))/SUM(BB-COALESCE(IBB,0)+COALESCE(HBP,0)+H) AS runPlus 
, SUM(H+BB-COALESCE(IBB,0)+COALESCE(HBP,0))/SUM(AB+BB-COALESCE(IBB,0)+COALESCE(HBP,0)+COALESCE(SF,0)) AS wOBA 
FROM 
RunValues r
INNER JOIN 
( 
  bdb.Batting b
  INNER JOIN 
  PrimPos p
  ON b.playerID = p.playerID 
  AND b.yearID = p.yearID 
) 
ON r.yearID = b.yearID 
GROUP BY 
r.yearID 
, r.RperOut 
, r.runBB 
, r.runHB 
, r.run1B 
, r.run2B 
, r.run3B 
, r.runHR 
, r.runSB 
, r.runCS 
ORDER BY 
r.yearID DESC; 


CREATE TABLE RunValues2 AS
SELECT yearID 
, RperOut 
, runBB 
, runHB 
, run1B 
, run2B 
, run3B 
, runHR 
, runSB 
, runCS 
, runMinus 
, runPlus 
, wOBA 
, @ws := 1/(runPlus+runMinus) AS wOBAscale 
, (runBB+runMinus)*@ws AS wobaBB 
, (runHB+runMinus)*@ws AS wobaHB 
, (run1B+runMinus)*@ws AS woba1B 
, (run2B+runMinus)*@ws AS woba2B 
, (run3B+runMinus)*@ws AS woba3B 
, (runHR+runMinus)*@ws AS wobaHR 
, runSB*@ws AS wobaSB 
, runCS*@ws AS wobaCS 
FROM RunValues1A;
