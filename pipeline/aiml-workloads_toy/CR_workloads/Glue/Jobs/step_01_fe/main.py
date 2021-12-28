print('Loading the required libraries')
import boto3
from datetime import  datetime 
from dateutil.relativedelta import relativedelta
from awsglue.utils import getResolvedOptions
import os
import sys
import pyspark.sql.functions as func
from awsglue.dynamicframe import DynamicFrame
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.sql.types import *
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from pyspark.sql import Window
import json
import ast
import gc
from pyspark.conf import SparkConf
from pyspark.ml.feature import StringIndexer

print('starting glue job')

args = getResolvedOptions(sys.argv, ['today', 'source_path', 'destination_path', 'kms_key_id'])
# settign varibles.
today = datetime.strptime(args['today'], '%Y-%m-%d').date()
updated_at  = today.strftime('%Y-%m-%d')
source_path = args['source_path']
destination_path = args['destination_path']
kms_key_id = args['kms_key_id']

spark_conf = SparkConf().setAll([
    ("spark.hadoop.fs.s3.enableServerSideEncryption", "true"),
    ("spark.hadoop.fs.s3.serverSideEncryption.kms.keyId", kms_key_id),
    ("spark.sql.sources.partitionOverwriteMode", "dynamic"),
    ("hive.metastore.client.factory.class", "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"),
    ("spark.sql.catalogImplementation", "hive"),
    ("hive.exec.dynamic.partition.mode", "nonstrict")
])
sc = SparkContext.getOrCreate(conf=spark_conf)
glueContext = GlueContext(sc)
spark = glueContext.spark_session
logger = glueContext.get_logger()

# read the csv.
df = glueContext.read.csv(source_path,header=True)
print(df.show())
# Formateo como fechas y ids. Deberia hacer QA por ejemplo fechas de laburo topearla a current date o cualquier otra estrategia.
df = df.withColumn("id", col('id').cast(IntegerType()))
df = df.withColumn("loan_id", col('loan_id').cast(IntegerType()))
df = df.withColumn("loan_amount", col('loan_amount').cast(DoubleType()))
df = df.withColumn("loan_date", to_date('loan_date','yyyy-MM-dd'))
df = df.withColumn("job_start_date", to_date('job_start_date','yyyy-MM-dd'))
# skip OutOfBoundsError in to_timestamp function dont see here. QA 
df = df.withColumn("job_start_date",when(col("job_start_date") > current_date(),current_date()).otherwise(col('job_start_date')))
df = df.withColumn("birthday", to_date('birthday','yyyy-MM-dd'))
# skip OutOfBoundsError in to_timestamp function dont see here. QA 
df = df.withColumn("birthday",when(col("birthday") > current_date(),current_date()).otherwise(col('birthday')))
# La convierto a long para poder usar estrategia de ventaneo.
df = df.withColumn("loan_date_ts", unix_timestamp(to_timestamp(col('loan_date'),'yyyy-MM-dd')))
# Declared processing_date.
df = df.withColumn("processing_date", lit(updated_at))

# Feature nb_previous_loans
df = df.withColumn("nb_previous_loans", dense_rank().over(Window.partitionBy("id").orderBy(asc("loan_date")))-1)

# avg_amount_loans_previous
w = Window.partitionBy('id')\
                 .orderBy(asc('loan_date_ts'))\
                 .rangeBetween(Window.unboundedPreceding, -1)
df = df.withColumn('avg_amount_loans_previous', mean('loan_amount').over(w))

# Reproduccion de la variable age. #TODO aplicar control de calidad sobre la columna.
df = df.withColumn("age",(datediff(current_date(), col('birthday'))/365.25).cast(IntegerType()))

# Ask DataScience better way to impute incorrect datos. For example bod or age > 100 years.
df = df.withColumn("years_on_the_job",(datediff(current_date(), col('job_start_date'))/365.25).cast(IntegerType()))

# De nuevo no hay control de calidad sobre los datos de entrada. Convendria mejor un OneHOt Encoder.
@udf(returnType=StringType()) 
def is_own_car(x):
    return  0 if x == 'N' else 1
df = df.withColumn("flag_own_car",is_own_car(col("flag_own_car")))

print(df.printSchema())

#exporting results to s3 into a parquet file (feature offline)

# Guardo en parquet (feature store offline) Discuss partitioning strategy. Take into account the refresh of old partitions
# in prod enviromment.
#TODO change strategy to  "feature online" (SQL database) upsert records instead.
# Uncomment if we decide to do partition over loan dates.(Historical retrive)
# df = df.repartition("loan_date")
#df.write.mode('overwrite')\
#        .format('parquet')\
#        .partitionBy('loan_date')\
#        .save(destination_path)
df.write.mode('overwrite')\
        .format('parquet')\
        .save(destination_path)

# online feature store replication
# TODO
