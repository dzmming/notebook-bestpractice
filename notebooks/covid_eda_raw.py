# Databricks notebook source
# MAGIC %md
# MAGIC #### Get latest COVID-19 hospitalization data

# COMMAND ----------

# MAGIC %md
# MAGIC #### Download data from the internet
# MAGIC https://docs.databricks.com/files/download-internet-files.html#language-bash
# MAGIC
# MAGIC a)these target files downloaded to the volume storage attached to the driver, use %sh to see these files. The current location for this data is in ephemeral volume storage that is only visible to the driver
# MAGIC b)Moving data with dbutils, The Databricks Utilities (dbutils) allow you to move files from volume storage attached to the driver to other locations accessible with the DBFS, including external object storage locations you’ve configured access to. 
# MAGIC c)After you move the data to cloud object storage, you can read the data as normal.
# MAGIC

# COMMAND ----------

# !wget -q https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/hospitalizations/covid-hospitalizations.csv -O /tmp/covid-hospitalizations.csv

!wget https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/hospitalizations/covid-hospitalizations.csv -O /tmp/covid-hospitalizations.csv

# COMMAND ----------

# MAGIC %sh 
# MAGIC curl https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/hospitalizations/covid-hospitalizations.csv --output /tmp/covid-hospitalizations.csv
# MAGIC

# COMMAND ----------

# MAGIC %sh
# MAGIC
# MAGIC pwd

# COMMAND ----------

# MAGIC %sh ls /tmp/

# COMMAND ----------

# MAGIC %sh ls /dbfs/tmp/

# COMMAND ----------

!wget  https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/hospitalizations/covid-hospitalizations.csv

#download to /Workspace/Repos/zhadeng@microsoft.com/notebook-bestpractice/notebooks  (os.getcwd())

# COMMAND ----------

# MAGIC %fs
# MAGIC ls /tmp
# MAGIC
# MAGIC

# COMMAND ----------



# COMMAND ----------


# dbutils.fs.mv("file:/tmp/covid-hospitalizations.csv", "dbfs:/tmp/covid-hospitalizations.csv")
dbutils.fs.cp("file:/tmp/covid-hospitalizations.csv", "dbfs:/tmp/covid-hospitalizations.csv")


# COMMAND ----------

# MAGIC %fs 
# MAGIC
# MAGIC rm /tmp/covid-hospitalizations.csv

# COMMAND ----------

df = spark.read.format("csv").option("header", True).load("/tmp/covid-hospitalizations.csv")
display(df)

# You can use Spark to read data files. You must provide Spark with the fully qualified path. Workspace files in Repos use the path file:/Workspace/Repos/<user_folder>/<repo_name>/file.

# COMMAND ----------



import os

print(os.getcwd())
df2 = spark.read.format("csv").load(f"file:{os.getcwd()}/covid-hospitalizations.csv")
display(df2)


# COMMAND ----------


# dbutils.fs.mv("file:/tmp/covid-hospitalizations.csv", "dbfs:/tmp/covid-hospitalizations.csv")
dbutils.fs.cp("file:/tmp/covid-hospitalizations.csv", "dbfs:/tmp/covid-hospitalizations.csv")

# COMMAND ----------

df = spark.read.format("csv").option("header", True).load("/tmp/covid-hospitalizations.csv")
display(df)

# COMMAND ----------

# MAGIC %md #### Transform

# COMMAND ----------

import pandas as pd

# read from /tmp, just is file:/tmp, not dbfs:/tmp, subset for USA, pivot and fill missing values
df = pd.read_csv("/tmp/covid-hospitalizations.csv")
df = df[df.iso_code == 'USA']\
     .pivot_table(values='value', columns='indicator', index='date')\
     .fillna(0)

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Visualize 

# COMMAND ----------

df.plot(figsize=(13,6), grid=True).legend(loc='upper left')

# COMMAND ----------

# MAGIC  %md
# MAGIC #### Save to Delta Lake
# MAGIC The current schema has spaces in the column names, which are incompatible with Delta Lake.  To save our data as a table, we'll replace the spaces with underscores.  We also need to add the date index as its own column or it won't be available to others who might query this table.

# COMMAND ----------

import pyspark.pandas as ps

# clean_cols = df.columns.str.replace(' ', '_')

# Create pandas on Spark dataframe
psdf = ps.from_pandas(df)

psdf.columns = clean_cols
psdf['date'] = psdf.index

# Write to Delta table, overwrite with latest data each time
psdf.to_table(name='dev_covid_analysis', mode='overwrite')

# COMMAND ----------

# MAGIC %md
# MAGIC #### View table

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM dev_covid_analysis
