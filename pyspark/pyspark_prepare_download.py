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
    # df_downloaded = spark.read.format('csv').options(header='true', delimiter='\t', inferschema='true').load(args.hdfs_source_dir + '/downloaded/*.tsv')
    
    
    # TODO: Remove all elements that are already downloaded
        
    # Select a random number of ids
    take = args.count
    count = df_ids.count()
    number = take if count > take else count    
    df_random = df_ids.sample(fraction=float(1.0*number/count)).limit(take)
    
    # Drop columns that are not needed
    cols_to_drop = ['insert_date']
    df_random = df_random.drop(*cols_to_drop)
    
    # Write data to HDFS
    df_random.show(5)
    
    df_random.write.format('csv').mode('overwrite').save(args.hdfs_target_dir)
        
    print("\n\n\n\n!!!!!!!!!!!!!!!!!!!! END !!!!!!!!!!!!!!!!!!!!!!!!\n\n\n\n")    
