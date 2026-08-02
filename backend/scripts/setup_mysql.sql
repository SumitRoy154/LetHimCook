CREATE DATABASE IF NOT EXISTS let_him_cook
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'let_him_cook'@'localhost' IDENTIFIED BY 'let_him_cook';
GRANT ALL PRIVILEGES ON let_him_cook.* TO 'let_him_cook'@'localhost';
FLUSH PRIVILEGES;
