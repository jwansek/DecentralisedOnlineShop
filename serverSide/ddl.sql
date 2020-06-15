CREATE DATABASE online_shop;
USE online_shop;

CREATE TABLE IF NOT EXISTS products (
    prod_id BIGINT UNSIGNED NOT NULL PRIMARY KEY,
    title VARCHAR(60) NULL,
    category VARCHAR(30) NULL,
    weight VARCHAR(8) NULL,
    price VARCHAR(8) NULL,
    quantity INT UNSIGNED NOT NULL,
    prod_info VARCHAR(1000) NULL,
    nutritional_info VARCHAR(1000) NULL,
    storage_info VARCHAR(1000) NULL
);

CREATE TABLE IF NOT EXISTS related_products (
    prod_id BIGINT UNSIGNED NOT NULL REFERENCES products (prod_id),
    related_id BIGINT UNSIGNED NOT NULL REFERENCES products (prod_id),
    PRIMARY KEY (prod_id, related_id)
);

CREATE TABLE IF NOT EXISTS images (
    prod_id BIGINT UNSIGNED NOT NULL REFERENCES products (prod_id),
    impath VARCHAR(23) NOT NULL,
    PRIMARY KEY (prod_id, impath)
);

CREATE TABLE IF NOT EXISTS releases (
    name VARCHAR(16) NOT NULL PRIMARY KEY,
    path VARCHAR(100) NOT NULL,
    torrent VARCHAR(24) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(30) NOT NULL,
    card_no CHAR(19) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL REFERENCES users (user_id),
    datetime DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id INT UNSIGNED NOT NULL REFERENCES orders (order_id),
    prod_id INT UNSIGNED NOT NULL REFERENCES products (product_id),
    quantity INT UNSIGNED NOT NULL,
    PRIMARY KEY (order_id, prod_id)
);


