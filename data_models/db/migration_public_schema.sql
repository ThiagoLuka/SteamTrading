
--DROP TABLE IF EXISTS public.asset_from_buy_order;
--DROP TABLE IF EXISTS public.buy_orders;
--DROP TABLE IF EXISTS public.sell_listing;
--DROP TABLE IF EXISTS public.item_steam_assets;
--DROP TABLE IF EXISTS public.item_trading_cards;
--DROP TABLE IF EXISTS public.item_steam_descriptions;
--DROP TABLE IF EXISTS public.items_steam;
--DROP TABLE IF EXISTS public.item_steam_types;
--DROP TABLE IF EXISTS public.user_badges;
--DROP TABLE IF EXISTS public.pure_badges;
--DROP TABLE IF EXISTS public.game_badges;
--DROP TABLE IF EXISTS public.user_game_trade;
--DROP TABLE IF EXISTS public.users;
--DROP TABLE IF EXISTS public.games;
--DROP SCHEMA IF EXISTS public;


--CREATE SCHEMA IF NOT EXISTS public;


-- game and users
CREATE TABLE IF NOT EXISTS public.steam_game (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, "name" text NOT NULL
	, market_id text NOT NULL
	, has_trading_cards bool NULL DEFAULT true
	, CONSTRAINT steam_game_pkey PRIMARY KEY (id)
	, CONSTRAINT steam_game_market_id_key UNIQUE (market_id)
);

CREATE TABLE IF NOT EXISTS public.steam_user (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, steam_id text NOT NULL
	, steam_alias text NULL
	, CONSTRAINT steam_user_pkey PRIMARY KEY (id)
	, CONSTRAINT steam_user_steam_id_key UNIQUE (steam_id)
);

CREATE TABLE IF NOT EXISTS public.steam_user_marketable_game (
	  user_id int4 NOT NULL
	, game_id int4 NOT NULL
	, CONSTRAINT user_game_trade_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
	, CONSTRAINT user_game_trade_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);


-- badges
CREATE TABLE IF NOT EXISTS public.game_badges (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, game_id int4 NOT NULL
	, "name" text NOT NULL
	, "level" int4 NOT NULL
	, foil bool NOT NULL
	, CONSTRAINT game_badges_pkey PRIMARY KEY (id)
	, CONSTRAINT game_badges_game_id_level_foil_key UNIQUE (game_id, level, foil)
	, CONSTRAINT game_badges_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
);

CREATE TABLE IF NOT EXISTS public.pure_badges (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, page_id int4 NOT NULL
	, "name" text NOT NULL
	, CONSTRAINT pure_badges_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.user_badges (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, user_id int4 NOT NULL
	, game_badge_id int4 NULL
	, pure_badge_id int4 NULL
	, experience int4 NULL
	, unlocked_at timestamp NULL
	, active bool NULL DEFAULT true
	, CONSTRAINT user_badges_pkey PRIMARY KEY (id)
	, CONSTRAINT user_badges_game_badge_id_fkey FOREIGN KEY (game_badge_id) REFERENCES public.game_badges(id)
	, CONSTRAINT user_badges_pure_badge_id_fkey FOREIGN KEY (pure_badge_id) REFERENCES public.pure_badges(id)
	, CONSTRAINT user_badges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);


-- item dimension
CREATE TABLE IF NOT EXISTS public.steam_item_type (
	  id int4 NOT NULL
	, "name" text NOT NULL
	, CONSTRAINT steam_item_type_pkey PRIMARY KEY (id)
	, CONSTRAINT steam_item_type_name_key UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS public.steam_item (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, game_id int4 NOT NULL
	, steam_item_type_id int4 NOT NULL
	, "name" text NOT NULL
	, market_url_name text NOT NULL
	, steam_item_name_id text NULL
	, CONSTRAINT steam_item_pkey PRIMARY KEY (id)
	, CONSTRAINT unique_steam_item UNIQUE (game_id, market_url_name)
	, CONSTRAINT steam_item_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
	, CONSTRAINT steam_item_steam_item_type_id_fkey FOREIGN KEY (steam_item_type_id) REFERENCES public.steam_item_type(id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS public.steam_item_description (
	  item_id int4 NOT NULL
	, class_id text NOT NULL
	, CONSTRAINT steam_item_description_pkey PRIMARY KEY (item_id)
	, CONSTRAINT unique_descript UNIQUE (class_id)
	, CONSTRAINT steam_item_description_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items_steam(id)
);

CREATE TABLE IF NOT EXISTS public.steam_trading_card (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, item_id int4 NOT NULL
	, game_id int4 NOT NULL
	, set_number int2 NOT NULL
	, foil bool NOT NULL DEFAULT false
	, CONSTRAINT steam_trading_card_pkey PRIMARY KEY (id)
	, CONSTRAINT unique_steam_trading_card UNIQUE (game_id, set_number, foil)
	, CONSTRAINT steam_trading_card_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
	, CONSTRAINT steam_trading_card_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items_steam(id)
);


-- inventory
CREATE TABLE IF NOT EXISTS public.steam_asset (
	  id int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (START WITH 3568000)
	, item_id int4 NOT NULL
	, user_id int4 NOT NULL
	, steam_asset_id text NOT NULL
	, active bool NOT NULL
	, marketable bool NOT NULL
	, tradable bool NOT NULL
	, origin text NOT NULL
	, origin_price int4 NOT NULL
	, destination text NOT NULL
	, destination_price int4 NOT NULL
	, created_at timestamp NOT NULL
	, removed_at timestamp NULL
	, CONSTRAINT steam_asset_pkey PRIMARY KEY (id)
	, CONSTRAINT unique_steam_asset UNIQUE (user_id, steam_asset_id)
	, CONSTRAINT steam_asset_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items_steam(id)
	, CONSTRAINT steam_asset_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);


-- sell listing
CREATE TABLE IF NOT EXISTS public.sell_listing (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, steam_sell_listing_id text NULL
	, asset_id int4 NOT NULL
	, user_id int4 NOT NULL
	, active bool NOT NULL
	, price_buyer int4 NOT NULL
	, price_to_receive int4 NOT NULL
	, steam_created_at date NOT NULL
	, created_at timestamp NOT NULL
	, removed_at timestamp NULL
	, CONSTRAINT sell_listing_pkey PRIMARY KEY (id)
	, CONSTRAINT sell_listing_steam_sell_listing_id_key UNIQUE (steam_sell_listing_id)
	, CONSTRAINT sell_listing_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.steam_asset(id)
	, CONSTRAINT sell_listing_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);


-- buy order
CREATE TABLE IF NOT EXISTS public.buy_order (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, steam_buy_order_id text NULL
	, user_id int4 NOT NULL
	, item_id int4 NOT NULL
	, active bool NOT NULL
	, price int4 NOT NULL
	, qtd_start int4 NOT NULL
	, qtd_current int4 NOT NULL
	, created_at timestamp NOT NULL
	, updated_at timestamp NOT NULL
	, removed_at timestamp NULL
	, CONSTRAINT buy_order_pkey PRIMARY KEY (buy_order_id)
	, CONSTRAINT buy_order_steam_buy_order_id_key UNIQUE (steam_buy_order_id)
	, CONSTRAINT buy_order_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items_steam(id)
	, CONSTRAINT buy_order_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);


-- inventory origin tables
CREATE TABLE IF NOT EXISTS public.asset_from_buy_order (
      asset_id int8 NOT NULL
    , buy_order_id int4 NOT NULL
    , CONSTRAINT asset_from_buy_order_asset_id UNIQUE (asset_id)
    , CONSTRAINT asset_from_buy_order_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.steam_asset(id)
    , CONSTRAINT asset_from_buy_order_buy_order_id_fkey FOREIGN KEY (buy_order_id) REFERENCES public.buy_order(id)
);

CREATE TABLE IF NOT EXISTS public.asset_from_booster_pack (
      asset_id int8 NOT NULL
    , booster_pack_asset_id int8 NOT NULL
    , CONSTRAINT asset_from_booster_pack_asset_id UNIQUE (asset_id)
    , CONSTRAINT asset_from_booster_pack_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.steam_asset(id)
    , CONSTRAINT asset_from_booster_pack_booster_pack_asset_id_id_fkey FOREIGN KEY (booster_pack_asset_id) REFERENCES public.steam_asset(id)
);
