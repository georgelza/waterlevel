
SELECT dateTimeFormat(time, 'YYYY-MM-DD HH:mm:ss') AS formatted_time, * FROM WaterTankLevels WHERE time > now() - 1h


SELECT time AS formatted_time, water_level, fill_percentage, water_volume, voltage,     value FROM CouncilWaterTank1 WHERE time > now() - 1h;



SELECT * FROM "WaterTankLevels" WHERE time > now() - 1h

SELECT * FROM "WaterTankLevels" WHERE time > now() - 1h and "tank"::tag = 'CouncilWaterTank1';
SELECT * FROM "WaterTankLevels" WHERE time > now() - 1h and "tank"::tag = 'RainWaterTank';





delete from "WaterTankLevels" WHERE "tank"::tag = 'CouncilWaterTanktest';