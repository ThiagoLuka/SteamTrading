
--DROP TABLE IF EXISTS lookup.buyer_to_seller_price;
--DROP SCHEMA IF EXISTS lookup;

CREATE SCHEMA IF NOT EXISTS lookup;


CREATE TABLE IF NOT EXISTS lookup.buyer_to_seller_price (
	  price_buyer INT
	, price_seller INT
);
