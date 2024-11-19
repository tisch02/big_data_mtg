CREATE EXTERNAL TABLE IF NOT EXISTS ids (
    id INT, 
    insert_date STRING, 
    set_name STRING
) COMMENT 'Card IDs that should be downloaded' ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\t' STORED AS TEXTFILE LOCATION '/user/hadoop/mtg/ids' TBLPROPERTIES ('skip.header.line.count' = '1');