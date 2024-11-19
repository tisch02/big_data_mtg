CREATE SCHEMA IF NOT EXISTS data;

CREATE TABLE
    IF NOT EXISTS data.cards (
        id INT PRIMARY KEY,
        name VARCHAR(256),
        type VARCHAR(256),
        mana_val INT,
        mana_cost VARCHAR(256),
        set VARCHAR(256),
        card_num INT,
        artist VARCHAR(256),
        text TEXT,
        story TEXT,
        url VARCHAR(1024),
        img VARCHAR(1024)
    );