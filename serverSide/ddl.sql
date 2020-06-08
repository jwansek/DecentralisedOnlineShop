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
    magnet VARCHAR(300) NOT NULL,
    torrent VARCHAR(24) NOT NULL
);



