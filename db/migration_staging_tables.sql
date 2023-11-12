
--DROP TABLE IF EXISTS staging.buy_order;
--DROP SCHEMA staging;

CREATE SCHEMA IF NOT EXISTS staging;


CREATE TABLE IF NOT EXISTS staging.buy_order
  (
	  steam_buy_order_id TEXT
	, item_id INT
	, user_id INT
	, price INT
	, quantity INT
   );
