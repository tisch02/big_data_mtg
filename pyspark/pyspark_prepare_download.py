import pyspark
from pyspark.sql import SparkSession
from pyspark import SparkContext
import argparse

def get_args():
    """
    Parses Command Line Args
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--hdfs_source_dir', required=True, type=str)
    parser.add_argument('--hdfs_target_dir', required=True, type=str)
    parser.add_argument('--count', required=True, type=int)
    return parser.parse_args()

if __name__ == '__main__':
    """
    Main Function
    """
    # Parse Command Line Args
    args = get_args()

    # Initialize Spark Context
    sc = pyspark.SparkContext()
    spark = SparkSession(sc)
    
    print("\n\n\n\n!!!!!!!!!!!!!!!!!!!! START !!!!!!!!!!!!!!!!!!!!!!\n\n\n\n")

    # Read ids from HDFS    
    df_ids = spark.read.format('csv').options(header='true', delimiter='\t', inferschema='true').load(args.hdfs_source_dir + '/ids/*.tsv')
    df_downloaded = spark.read.format('csv').options(header='true', delimiter=',', inferschema='true').load(args.hdfs_source_dir + '/downloaded/*.csv')    
    
    # Remove all elements that are already downloaded
    cols = ['id', 'set_name']
    id_dif = df_ids.select(*cols).subtract(df_downloaded.select(*cols)).collect()    
    
    # Select firt n elements of list
    num = int(args.count)
    if int(args.count) > len(id_dif):
        num = len(id_dif)
    
    df_result = spark.createDataFrame(id_dif[0:num])
    
    # Write result    
    df_result.write.format('csv').options(header='True').mode('overwrite').save(args.hdfs_target_dir)
    
    print("\n\n\n\n!!!!!!!!!!!!!!!!!!!! END !!!!!!!!!!!!!!!!!!!!!!!!\n\n\n\n")    
    df_result.show()
