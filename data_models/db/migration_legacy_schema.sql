
--DROP TABLE IF EXISTS legacy.item_booster_packs
--DROP SCHEMA IF EXISTS legacy;


CREATE SCHEMA IF NOT EXISTS legacy;


CREATE TABLE IF NOT EXISTS legacy.item_booster_packs (
	id int4 NULL,
	item_steam_id int4 NULL,
	game_id int4 NULL,
	times_opened int4 NULL,
	foil_quantity int4 NULL
);