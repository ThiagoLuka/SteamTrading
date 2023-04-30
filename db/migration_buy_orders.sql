
--DROP TABLE IF EXISTS buy_orders;


 CREATE TABLE IF NOT EXISTS buy_orders
  (
  	  buy_order_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
  	, steam_buy_order_id TEXT UNIQUE
  	, user_id INT NOT NULL REFERENCES users(id)
  	, item_steam_id INT NOT NULL REFERENCES items_steam(id)
  	, active BOOL NOT NULL
  	, price INT NOT NULL
  	, qtd_start INT NOT NULL
  	, qtd_estimate INT NOT NULL
  	, qtd_current INT NOT NULL
  	, created_at TIMESTAMP NOT NULL
  	, updated_at TIMESTAMP NOT NULL
  	, removed_at TIMESTAMP
  );
