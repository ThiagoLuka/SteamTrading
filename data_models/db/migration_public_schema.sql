
--DROP TABLE IF EXISTS public.buy_orders;
--DROP TABLE IF EXISTS public.sell_listing;
--DROP TABLE IF EXISTS public.item_steam_assets;
--DROP TABLE IF EXISTS public.item_booster_packs;
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
CREATE TABLE public.games (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, "name" text NOT NULL
	, market_id text NOT NULL
	, has_trading_cards bool NULL DEFAULT true
	, CONSTRAINT games_pkey PRIMARY KEY (id)
	, CONSTRAINT games_market_id_key UNIQUE (market_id)
);

CREATE TABLE public.users (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, steam_id text NOT NULL
	, steam_alias text NULL
	, CONSTRAINT users_pkey PRIMARY KEY (id)
	, CONSTRAINT users_steam_id_key UNIQUE (steam_id)
);

CREATE TABLE public.user_game_trade (
	  user_id int4 NOT NULL
	, game_id int4 NOT NULL
	, CONSTRAINT user_game_trade_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
	, CONSTRAINT user_game_trade_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);


-- badges
CREATE TABLE public.game_badges (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, game_id int4 NOT NULL
	, "name" text NOT NULL
	, "level" int4 NOT NULL
	, foil bool NOT NULL
	, CONSTRAINT game_badges_pkey PRIMARY KEY (id)
	, CONSTRAINT game_badges_game_id_level_foil_key UNIQUE (game_id, level, foil)
	, CONSTRAINT game_badges_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
);

CREATE TABLE public.pure_badges (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, page_id int4 NOT NULL
	, "name" text NOT NULL
	, CONSTRAINT pure_badges_pkey PRIMARY KEY (id)
);

CREATE TABLE public.user_badges (
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
CREATE TABLE public.item_steam_types (
	  id int4 NOT NULL
	, "name" text NOT NULL
	, CONSTRAINT item_steam_types_pkey PRIMARY KEY (id)
	, CONSTRAINT item_steam_types_name_key UNIQUE (name)
);

CREATE TABLE public.items_steam (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, game_id int4 NOT NULL
	, item_steam_type_id int4 NOT NULL
	, "name" text NOT NULL
	, market_url_name text NOT NULL
	, CONSTRAINT items_steam_pkey PRIMARY KEY (id)
	, CONSTRAINT unique_item UNIQUE (game_id, market_url_name)
	, CONSTRAINT items_steam_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
	, CONSTRAINT items_steam_item_steam_type_id_fkey FOREIGN KEY (item_steam_type_id) REFERENCES public.item_steam_types(id) ON UPDATE CASCADE
);

CREATE TABLE public.item_steam_descriptions (
	  item_steam_id int4 NOT NULL
	, class_id text NOT NULL
	, CONSTRAINT item_steam_descriptions_pkey PRIMARY KEY (item_steam_id)
	, CONSTRAINT unique_descript UNIQUE (class_id)
	, CONSTRAINT item_steam_descriptions_item_steam_id_fkey FOREIGN KEY (item_steam_id) REFERENCES public.items_steam(id)
);

CREATE TABLE public.item_trading_cards (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, item_steam_id int4 NOT NULL
	, game_id int4 NOT NULL
	, set_number int2 NOT NULL
	, foil bool NOT NULL DEFAULT false
	, CONSTRAINT item_trading_cards_pkey PRIMARY KEY (id)
	, CONSTRAINT unique_card UNIQUE (game_id, set_number, foil)
	, CONSTRAINT item_trading_cards_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
	, CONSTRAINT item_trading_cards_item_steam_id_fkey FOREIGN KEY (item_steam_id) REFERENCES public.items_steam(id) ON DELETE CASCADE
);

CREATE TABLE public.item_booster_packs (  -- no longer used
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, item_steam_id int4 NOT NULL
	, game_id int4 NOT NULL
	, times_opened int4 NOT NULL DEFAULT 0
	, foil_quantity int4 NOT NULL DEFAULT 0
	, CONSTRAINT item_booster_packs_pkey PRIMARY KEY (id)
	, CONSTRAINT unique_pack UNIQUE (game_id)
	, CONSTRAINT item_booster_packs_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id)
	, CONSTRAINT item_booster_packs_item_steam_id_fkey FOREIGN KEY (item_steam_id) REFERENCES public.items_steam(id) ON DELETE CASCADE
);


-- inventory
CREATE TABLE public.item_steam_assets (
	  id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, item_steam_id int4 NOT NULL
	, user_id int4 NOT NULL
	, asset_id text NOT NULL
	, marketable bool NOT NULL
	, created_at timestamp NOT NULL
	, removed_at timestamp NULL
	, CONSTRAINT item_steam_assets_pkey PRIMARY KEY (id)
	, CONSTRAINT unique_asset UNIQUE (user_id, asset_id)
	, CONSTRAINT item_steam_assets_item_steam_id_fkey FOREIGN KEY (item_steam_id) REFERENCES public.items_steam(id)
	, CONSTRAINT item_steam_assets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);


-- sell listing
CREATE TABLE public.sell_listing (
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
	, CONSTRAINT sell_listing_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.item_steam_assets(id)
	, CONSTRAINT sell_listing_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);


-- buy order
CREATE TABLE public.buy_orders (
	  buy_order_id int4 NOT NULL GENERATED ALWAYS AS IDENTITY
	, steam_buy_order_id text NULL
	, user_id int4 NOT NULL
	, item_steam_id int4 NOT NULL
	, active bool NOT NULL
	, price int4 NOT NULL
	, qtd_start int4 NOT NULL
	, qtd_estimate int4 NOT NULL
	, qtd_current int4 NOT NULL
	, created_at timestamp NOT NULL
	, updated_at timestamp NOT NULL
	, removed_at timestamp NULL
	, CONSTRAINT buy_orders_pkey PRIMARY KEY (buy_order_id)
	, CONSTRAINT buy_orders_steam_buy_order_id_key UNIQUE (steam_buy_order_id)
	, CONSTRAINT buy_orders_item_steam_id_fkey FOREIGN KEY (item_steam_id) REFERENCES public.items_steam(id)
	, CONSTRAINT buy_orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
