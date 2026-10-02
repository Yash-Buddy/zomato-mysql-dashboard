CREATE DATABASE IF NOT EXISTS zomato_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE zomato_db;

DROP TABLE IF EXISTS restaurants;
CREATE TABLE restaurants (
  restaurant_id        INT PRIMARY KEY,
  restaurant_name      VARCHAR(255),
  country_code         INT,
  city                 VARCHAR(100),
  address              VARCHAR(500),
  locality             VARCHAR(255),
  locality_verbose     VARCHAR(500),
  longitude            DECIMAL(10,6),
  latitude             DECIMAL(10,6),
  cuisines             VARCHAR(500),
  avg_cost_for_two     INT,
  currency             VARCHAR(50),
  has_table_booking    VARCHAR(3),
  has_online_delivery  VARCHAR(3),
  is_delivering_now    VARCHAR(3),
  price_range          TINYINT,
  aggregate_rating     DECIMAL(2,1),
  rating_color         VARCHAR(20),
  rating_text          VARCHAR(20),
  votes                INT,
  INDEX idx_city (city),
  INDEX idx_rating (aggregate_rating)
);
