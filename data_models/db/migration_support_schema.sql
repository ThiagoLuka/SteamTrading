
--DROP TABLE IF EXISTS lookup.steam_all_apps;
--DROP TABLE IF EXISTS lookup.buyer_to_seller_price;
--DROP SCHEMA IF EXISTS lookup;

CREATE SCHEMA IF NOT EXISTS lookup;


CREATE TABLE IF NOT EXISTS lookup.buyer_to_seller_price (
	  price_buyer INT
	, price_seller INT
);

CREATE TABLE IF NOT EXISTS lookup.steam_all_apps (
      app_id text NOT NULL
    , request_success bool NOT NULL
    , name text
    , processed bool
    , app_type text
    , full_game_app_id text
    , has_cards bool
    , coming_soon bool
    , release_date text
	, CONSTRAINT steam_all_apps_pkey PRIMARY KEY (app_id)
);
