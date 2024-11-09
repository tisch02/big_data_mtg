# Big Data - MTG

[GitHub Repo](https://github.com/marcelmittelstaedt/BigData/)

## Setup
1. `py -m venv env`
2. `env\Scripts\activate`


## Get file from HDFS 
curl "http://34e0454c2314:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=hadoop:9000&offset=0"
curl "http://34e0454c2314:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=34.89.168.124:9000&offset=0"


curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=hadoop:9000"
http://34.89.168.124:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=34.89.168.124:9000

http://34.89.168.124/
curl -i -X PUT "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/sets/test.txt?op=CREATE&namenoderpcaddress=hadoop:9000"

curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=CREATE
                    [&overwrite=<true|false>][&blocksize=<LONG>][&replication=<SHORT>]
                    [&permission=<OCTAL>][&buffersize=<INT>]"
    