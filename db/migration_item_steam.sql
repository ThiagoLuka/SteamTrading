 
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
 	,market_item_name_id TEXT UNIQUE
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
	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
	,item_steam_id INT NOT NULL REFERENCES items_steam(id)
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
	,removed_at TIMESTAMP NOT NULL
	,CONSTRAINT unique_asset UNIQUE(asset_id)
);
