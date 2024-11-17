# Big Data - MTG

[GitHub Repo](https://github.com/marcelmittelstaedt/BigData/)

## Setup
1. `py -m venv env`
2. `env\Scripts\activate`


## Get file from HDFS 
curl "http://34e0454c2314:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=hadoop:9000&offset=0"
curl "http://34e0454c2314:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=34.89.168.124:9000&offset=0"


part-00000-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/_SUCCESS?op=OPEN&namenoderpcaddress=hadoop:9000"
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/part-00000-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv?op=OPEN&namenoderpcaddress=hadoop:9000"
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/part-00001-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv?op=OPEN&namenoderpcaddress=hadoop:9000"
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/part-00002-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv?op=OPEN&namenoderpcaddress=hadoop:9000"
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/part-00003-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv?op=OPEN&namenoderpcaddress=hadoop:9000"


curl "http://35.198.76.213:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=35.198.76.213:9000"

http://34.89.168.124/
curl -i -X PUT "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/sets/test.txt?op=CREATE&namenoderpcaddress=hadoop:9000"

curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=CREATE
                    [&overwrite=<true|false>][&blocksize=<LONG>][&replication=<SHORT>]
                    [&permission=<OCTAL>][&buffersize=<INT>]"


curl -i -X DELETE http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/ids/set_ids_230cd64a-88fc-4ef6-a531-e2edcae528d3.tsv?user.name=hadoop&op=DELETE&recursive=true&namenoderpcaddress=hadoop:9000
curl -i -X PUT    "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/sets/test.txt?op=CREATE&namenoderpcaddress=hadoop:9000"

curl -X GET "http://35.198.76.213:9864/webhdfs/v1/user/hadoop/mtg/todownload?op=LISTSTATUS&recursive=true"
curl -X GET "http://erie1.example.com:50070/webhdfs/v1/user/admin?op=LISTSTATUS&recursive=true"

## TODO
1. Download and put downloaded cards IDs into HDFS
2. When preparing download ids, subtract downloaded cards


    