CREATE EXTERNAL TABLE IF NOT EXISTS downloaded(	
    id INT,    
    set_name STRING
) COMMENT 'Card IDs that are already downloaded' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hadoop/mtg/downloaded' TBLPROPERTIES ('skip.header.line.count'='1');