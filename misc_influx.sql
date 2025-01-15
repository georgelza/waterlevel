
SELECT * FROM "WaterTankLevels" WHERE time > now() - 1h

SELECT dateTimeFormat(time, 'YYYY-MM-DD HH:mm:ss') AS formatted_time, * FROM WaterTankLevels WHERE time > now() - 1h

SELECT mean("fill_percentage") FROM "WaterTankLevels" WHERE "tank"::tag = 'CouncilWaterTank1' AND time >= 1736244962720ms and time <= 1736849762720ms GROUP BY time(10m) fill(null) ORDER BY time ASC

SELECT mean("fill_percentage") FROM WaterTankLevels WHERE time > now() - 1h




select * from "WaterTankLevels" where tag ="CouncilWaterTank1"  and time > now() - 1h;

select * from "WaterTankLevels" where tag ="RainWaterTank1"



SELECT time AS formatted_time, water_level, fill_percentage, water_volume, voltage,     value FROM CouncilWaterTank1 WHERE time > now() - 1h;