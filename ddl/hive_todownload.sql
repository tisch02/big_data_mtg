CREATE EXTERNAL TABLE IF NOT EXISTS todownload(	
    id INT,    
    set_name STRING
) COMMENT 'Card IDs that are ready for download' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hadoop/mtg/todownload' TBLPROPERTIES ('skip.header.line.count'='1');