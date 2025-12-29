CREATE DATABASE trading_platform;

\c trading_platform;

CREATE TYPE account_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE trade_type AS ENUM ('buy', 'sell');
CREATE TYPE trade_status AS ENUM ('completed', 'cancelled', 'pending');

CREATE TABLE user_profiles (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    registration_date TIMESTAMP,
    last_login TIMESTAMP,
    wallet_balance DECIMAL(15, 2),
    account_status account_status,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trades_real (
    trade_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    symbol VARCHAR(20),
    trade_type trade_type,
    amount DECIMAL(15, 2),
    price DECIMAL(15, 2),
    trade_date TIMESTAMP,
    status trade_status,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

CREATE TABLE trades_demo (
    trade_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    symbol VARCHAR(20),
    trade_type trade_type,
    amount DECIMAL(15, 2),
    price DECIMAL(15, 2),
    trade_date TIMESTAMP,
    status trade_status,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
); 