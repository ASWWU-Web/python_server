CREATE TABLE IF NOT EXISTS main.newprofiles AS SELECT * FROM main.profiles WHERE 0;

DROP TABLE main.profiles;

ALTER TABLE main.newprofiles RENAME TO profiles;