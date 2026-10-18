CREATE TABLE `just-program-384022.INTEGRATION.integration_prueba_tecnica` (
  id              INT64 NOT NULL,
  name            STRING,
  air_date        DATE,
  season          INT64,
  episode         INT64,
  url             STRING,
  created         TIMESTAMP,
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1, 21, 1))


BEGIN TRANSACTION;

DELETE FROM `just-program-384022.INTEGRATION.integration_prueba_tecnica`
WHERE id IN (
  SELECT DISTINCT id FROM `just-program-384022.RAW.SANDBOX_RICK_MORTY`
);

INSERT INTO `just-program-384022.INTEGRATION.integration_prueba_tecnica`
  (id, name, air_date, season, episode, url, created)
SELECT
  id,
  name,
  SAFE.PARSE_DATE('%B %d, %Y', air_date),
  SAFE_CAST(REGEXP_EXTRACT(episode, r'S(\d+)') AS INT64),
  SAFE_CAST(REGEXP_EXTRACT(episode, r'E(\d+)') AS INT64),
  url,
  created
FROM `just-program-384022.RAW.SANDBOX_RICK_MORTY`
ORDER BY id asc;

COMMIT;