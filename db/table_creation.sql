

CREATE TABLE IF NOT EXISTS users
 (
 	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 	steam_id TEXT NOT NULL UNIQUE,
 	steam_alias TEXT
 );

CREATE TABLE IF NOT EXISTS games
 (
 	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 	name TEXT NOT NULL,
 	market_id TEXT NOT NULL UNIQUE
 );

CREATE TABLE IF NOT EXISTS game_badges
 (
 	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 	game_id INT REFERENCES games NOT NULL,
 	name TEXT NOT NULL,
 	level INT NOT NULL,
 	foil BOOL NOT NULL,
 	UNIQUE (game_id, level, foil)
 );

CREATE TABLE IF NOT EXISTS pure_badges
 (
 	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 	page_id INT NOT NULL,
 	name TEXT NOT NULL
 );

CREATE TABLE IF NOT EXISTS user_badges
  (
 	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 	user_id INT REFERENCES users NOT NULL,
 	game_badge_id INT REFERENCES game_badges,
 	pure_badge_id INT REFERENCES pure_badges,
 	experience INT,
 	unlocked_at TIMESTAMP
  );

ALTER TABLE user_badges
    ADD COLUMN IF NOT EXISTS active BOOL DEFAULT True;

CREATE TABLE IF NOT EXISTS trading_cards
  (
 	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 	game_id INT REFERENCES games NOT NULL,
 	set_number SMALLINT NOT NULL,
  	name TEXT NOT NULL,
  	url_name TEXT,
  	UNIQUE (game_id, set_number)
  );

CREATE TABLE IF NOT EXISTS item_types
  (
  	id INT PRIMARY KEY,
  	name TEXT NOT NULL
  );

CREATE TABLE IF NOT EXISTS item_descriptions
  (
 	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 	game_id INT REFERENCES games,
 	class_id TEXT NOT NULL UNIQUE,
 	type_id INT REFERENCES item_types NOT NULL,
 	name TEXT NOT NULL,
 	url_name TEXT
  );

CREATE TABLE IF NOT EXISTS item_assets
  (
   	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   	user_id INT REFERENCES users NOT NULL,
   	description_id INT REFERENCES item_descriptions NOT NULL,
   	asset_id TEXT NOT NULL,
   	created_at DATE NOT NULL
  );

ALTER TABLE item_assets
	ALTER COLUMN created_at TYPE TIMESTAMP,
	ADD COLUMN removed_at TIMESTAMP;