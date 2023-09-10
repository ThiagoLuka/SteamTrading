
--DROP TABLE IF EXISTS public.sell_listing;
--DROP TABLE IF EXISTS staging.sell_listing;
--DROP SCHEMA staging;


 CREATE TABLE IF NOT EXISTS public.sell_listing
  (
	  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
	, steam_sell_listing_id TEXT UNIQUE
	, asset_id INT NOT NULL REFERENCES item_steam_assets(id)
	, user_id INT NOT NULL REFERENCES users(id)
	, active BOOL NOT NULL
	, price_buyer INT NOT NULL
	, price_to_receive INT NOT NULL
	, steam_created_at DATE NOT NULL
	, created_at TIMESTAMP NOT NULL
	, removed_at TIMESTAMP
   );


CREATE SCHEMA IF NOT EXISTS staging;


CREATE TABLE IF NOT EXISTS staging.sell_listing
  (
	  steam_sell_listing_id TEXT
	, steam_asset_id TEXT
	, user_id INT
	, price_buyer INT
	, price_to_receive INT
	, steam_created_at DATE
	, created_at TIMESTAMP DEFAULT NOW()::TIMESTAMP
   );
