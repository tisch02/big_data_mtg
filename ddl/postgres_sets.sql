CREATE SCHEMA IF NOT EXISTS data;

CREATE TABLE
    IF NOT EXISTS data.sets (
        name VARCHAR(256) PRIMARY KEY, 
        downloaded BOOL
    );