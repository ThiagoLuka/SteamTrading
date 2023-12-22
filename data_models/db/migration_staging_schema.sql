
--DROP TABLE IF EXISTS staging.steam_badge;
--DROP TABLE IF EXISTS staging.steam_asset;
--DROP TABLE IF EXISTS staging.staging.steam_item_from_inventory;
--DROP TABLE IF EXISTS staging.steam_item_from_profile_game_cards;
--DROP TABLE IF EXISTS staging.game;
--DROP TABLE IF EXISTS staging.buy_order;
--DROP TABLE IF EXISTS staging.sell_listing;
--DROP SCHEMA IF EXISTS staging;

CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.buy_order (
	  steam_buy_order_id TEXT
	, item_id INT
	, user_id INT
	, price INT
	, quantity INT
	, created_at TIMESTAMP DEFAULT NOW()::TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.game (
      name TEXT
	, market_id TEXT
	, has_trading_cards BOOL
);

CREATE TABLE IF NOT EXISTS staging.steam_item_from_inventory (
	  game_market_id TEXT
	, market_url_name TEXT
	, name TEXT
	, steam_item_type_id INT
	, steam_item_type_name TEXT
	, class_id TEXT
);

CREATE TABLE IF NOT EXISTS staging.steam_item_from_profile_game_cards (
	  game_market_id TEXT
	, market_url_name TEXT
	, name TEXT
	, steam_item_type_id INT
	, set_number INT
	, foil BOOL
);

CREATE TABLE IF NOT EXISTS staging.steam_asset (
	  class_id TEXT
	, user_id INT
	, steam_asset_id TEXT
	, marketable BOOL
	, tradable BOOL
	, created_at TIMESTAMP DEFAULT NOW()::TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.steam_badge (
	  name TEXT
	, level INT
	, foil BOOL
	, game_market_id TEXT
	, pure_badge_page_id INT
	, experience INT
	, unlocked_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.sell_listing (
	  steam_sell_listing_id TEXT
	, steam_asset_id TEXT
	, user_id INT
	, price_buyer INT
	, price_to_receive INT
	, steam_created_at DATE
	, created_at TIMESTAMP DEFAULT NOW()::TIMESTAMP
);
