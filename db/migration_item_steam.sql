 
--DROP TABLE IF EXISTS item_steam_assets;
--DROP TABLE IF EXISTS item_steam_descriptions;
--DROP TABLE IF EXISTS item_booster_packs;
--DROP TABLE IF EXISTS item_trading_cards;
--DROP TABLE IF EXISTS items_steam;
--DROP TABLE IF EXISTS item_steam_types;

 ALTER TABLE games
 	ADD COLUMN IF NOT EXISTS has_trading_cards BOOL DEFAULT True;

 CREATE TABLE IF NOT EXISTS item_steam_types
  (
  	id INT PRIMARY KEY
  	,name TEXT NOT NULL UNIQUE
  );

 CREATE TABLE IF NOT EXISTS items_steam
 (
 	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
 	,game_id INT REFERENCES games(id) NOT NULL
 	,item_steam_type_id INT NOT NULL REFERENCES item_steam_types(id) ON UPDATE CASCADE
 	,name TEXT NOT NULL
 	,market_url_name TEXT NOT NULL
 	,CONSTRAINT unique_item UNIQUE(game_id, market_url_name)
 );

CREATE TABLE IF NOT EXISTS item_trading_cards
(
	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
	,item_steam_id INT NOT NULL REFERENCES items_steam(id) ON DELETE CASCADE
	,game_id INT NOT NULL REFERENCES games(id)
	,set_number SMALLINT NOT NULL
	,foil BOOL NOT NULL DEFAULT False
	,CONSTRAINT unique_card UNIQUE(game_id, set_number, foil)
);

CREATE TABLE IF NOT EXISTS item_booster_packs
(
	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
	,item_steam_id INT NOT NULL REFERENCES items_steam(id) ON DELETE CASCADE
	,game_id INT NOT NULL REFERENCES games(id)
	,times_opened INT NOT NULL DEFAULT 0
	,foil_rate DOUBLE PRECISION NOT NULL DEFAULT 0
	,CONSTRAINT unique_pack UNIQUE(game_id)
);

CREATE TABLE IF NOT EXISTS item_steam_descriptions
(
	item_steam_id INT NOT NULL REFERENCES items_steam(id) PRIMARY KEY
	,class_id TEXT NOT NULL
	,CONSTRAINT unique_descript UNIQUE(class_id)
);

CREATE TABLE IF NOT EXISTS item_steam_assets
(
	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
	,item_steam_id INT NOT NULL REFERENCES items_steam(id)
	,user_id INT NOT NULL REFERENCES users(id)
	,asset_id TEXT NOT NULL
	,marketable BOOL NOT NULL
	,created_at TIMESTAMP NOT NULL
	,removed_at TIMESTAMP
	,CONSTRAINT unique_asset UNIQUE(user_id, asset_id)
);


-- the next two queries insert item definitions that went through the old inventory
WITH old_descript_data AS (
	SELECT * FROM item_descriptions
	WHERE
		(game_id, url_name) NOT IN (
			SELECT game_id, market_url_name
			FROM items_steam
		)
)
INSERT INTO items_steam (
	game_id
	, item_steam_type_id
	, name
	, market_url_name
)
SELECT
	game_id
	, type_id
	, name
	, url_name
FROM old_descript_data;


WITH old_descript_data AS (
	SELECT *
	FROM item_descriptions
	WHERE
		(class_id) NOT IN (
			SELECT class_id
			FROM item_steam_descriptions isd
		)
)
INSERT INTO item_steam_descriptions (
	item_steam_id
	, class_id
)
SELECT
	is2.id
	, odd.class_id
FROM old_descript_data odd, items_steam is2
WHERE
	is2.game_id = odd.game_id
	AND is2.market_url_name = odd.url_name;


-- fixing created_at data at the new table
WITH old_created_at_data AS (
	SELECT
		new_a.id AS id
		, old_a.created_at AS old_created
		, new_a.created_at AS new_created
	FROM item_assets old_a
	FULL OUTER JOIN item_steam_assets new_a
		ON old_a.user_id = new_a.user_id AND old_a.asset_id = new_a.asset_id
	WHERE old_a.created_at IS NOT NULL
)
UPDATE item_steam_assets isa
SET created_at = old_c.old_created
FROM old_created_at_data old_c
WHERE isa.id = old_c.id;


-- insert old assets data into the new table
WITH old_assets_data AS (
	SELECT
		is2.id AS item_steam_id
		, old_a.user_id
		, old_a.asset_id
		, old_a.marketable
		, old_a.created_at
		, old_a.removed_at
	FROM item_assets old_a
	FULL OUTER JOIN item_steam_assets new_a
		ON old_a.user_id = new_a.user_id AND old_a.asset_id = new_a.asset_id
	INNER JOIN item_descriptions old_d
		ON old_a.description_id = old_d.id
	INNER JOIN items_steam is2
		ON is2.game_id = old_d.game_id AND is2.market_url_name = old_d.url_name
	WHERE new_a.id IS NULL
)
INSERT INTO item_steam_assets (
	item_steam_id
	, user_id
	, asset_id
	, marketable
	, created_at
	, removed_at
)
SELECT * FROM old_assets_data;
