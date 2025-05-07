import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, monotonically_increasing_id, to_date, year, month, quarter, dayofmonth, dayofweek, weekofyear, date_format
from pyspark.sql.types import IntegerType, StringType, DateType, DecimalType, TimestampType

# Get job arguments
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'RAW_S3_PATH',             # e.g., 's3://your-bucket/data/raw/'
    'PROCESSED_S3_PATH',       # e.g., 's3://your-bucket/data/processed/'
    'TEMP_S3_DIR',             # e.g., 's3://your-bucket/glue-scripts/temp/'
    'REDSHIFT_JDBC_URL',       # e.g., 'jdbc:redshift://your-cluster.xxxx.region.redshift.amazonaws.com:5439/your_db'
    'REDSHIFT_USER',           # Your Redshift master username or a dedicated ETL user
    'REDSHIFT_IAM_ROLE',       # IAM Role for Redshift to COPY from S3
    # 'REDSHIFT_PASSWORD_SECRET_NAME' # Optional: AWS Secrets Manager secret name for password
    # Add other parameters as needed
])

# Initialize Spark and Glue contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Define paths and Redshift connection properties
raw_s3_path = args['RAW_S3_PATH']
processed_s3_path = args['PROCESSED_S3_PATH']
temp_s3_dir = args['TEMP_S3_DIR']
redshift_jdbc_url = args['REDSHIFT_JDBC_URL']
redshift_user = args['REDSHIFT_USER']
# redshift_password = get_secret(args['REDSHIFT_PASSWORD_SECRET_NAME']) # Function to get secret
redshift_iam_role = args['REDSHIFT_IAM_ROLE']

# --- Placeholder for a function to retrieve password from AWS Secrets Manager ---
# def get_secret(secret_name):
#     import boto3
#     client = boto3.client('secretsmanager')
#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#     except ClientError as e:
#         # Handle error
#         raise e
#     else:
#         if 'SecretString' in get_secret_value_response:
#             secret = get_secret_value_response['SecretString']
#             return json.loads(secret)['password'] # Assuming password is json key
#         else:
#             # Handle binary secret if needed
#             pass

redshift_conn_options = {
    "url": redshift_jdbc_url,
    "user": redshift_user,
    # "password": redshift_password, # Use if not using IAM role for temp creds or direct JDBC password
    "dbtable": "public.placeholder", # Will be overridden for each table
    "aws_iam_role": redshift_iam_role, # For COPY command
    "tempdir": temp_s3_dir
}

logger = glueContext.get_logger()

logger.info(f"Starting ETL job: {args['JOB_NAME']}")
logger.info(f"Raw S3 Path: {raw_s3_path}")
logger.info(f"Processed S3 Path: {processed_s3_path}")


def load_and_write_to_redshift(df, table_name):
    logger.info(f"Writing table {table_name} to Redshift...")
    # Write to S3 as Parquet (intermediate step for Redshift COPY)
    output_path = f"{processed_s3_path}{table_name}"
    df.write.mode("overwrite").parquet(output_path)
    logger.info(f"Successfully wrote {table_name} to {output_path} in Parquet format.")

    # Load into Redshift using COPY command (via Glue connector)
    # The Glue connector for Redshift handles the COPY command implicitly when using an IAM role.
    # Ensure the Redshift table schema matches the DataFrame schema.
    redshift_table_options = redshift_conn_options.copy()
    redshift_table_options["dbtable"] = f"public.{table_name}" # Assuming public schema

    # It's often more reliable to use preactions to TRUNCATE if you are doing full reloads
    # and postactions for VACUUM and ANALYZE.
    # For production, consider upsert logic or incremental loads.
    preactions = f"TRUNCATE TABLE public.{table_name};"
    # postactions = f"VACUUM SORT ONLY public.{table_name}; ANALYZE public.{table_name};"

    glueContext.write_dynamic_frame_from_jdbc_conf(
        frame=DynamicFrame.fromDF(df, glueContext, f"{table_name}_dynamic_frame"),
        catalog_connection=None, # Not using Glue Catalog connection here, direct JDBC
        connection_options=redshift_table_options,
        redshift_tmp_dir=temp_s3_dir,
        transformation_ctx=f"write_{table_name}_to_redshift",
        # catalog_table_name=f"public.{table_name}" # If using catalog
        # preactions=preactions # Use with caution, TRUNCATE deletes all data
    )
    logger.info(f"Successfully initiated load of {table_name} into Redshift.")

try:
    # 1. Read Raw Data from S3
    logger.info("Reading raw transactions data...")
    transactions_df = spark.read.option("header", "true").option("inferSchema", "true").csv(f"{raw_s3_path}transactions.csv")
    logger.info("Reading raw budget data...")
    budget_df = spark.read.option("header", "true").option("inferSchema", "true").csv(f"{raw_s3_path}budget.csv")

    transactions_df.printSchema()
    budget_df.printSchema()

    # --- 2. Transformations and Dimension Creation ---
    logger.info("Starting transformations and dimension creation...")

    # Create DimDate
    # For a real scenario, use a more robust date dimension generation logic
    # This is a very simplified example. Consider pre-generating DimDate or using a date generation utility.
    min_date_trans = transactions_df.selectExpr("min(to_date(Date, 'yyyy-MM-dd')) as min_d").collect()[0]["min_d"]
    max_date_trans = transactions_df.selectExpr("max(to_date(Date, 'yyyy-MM-dd')) as max_d").collect()[0]["max_d"]
    # min_date_budget = budget_df.selectExpr("min(to_date(Period, 'yyyy-MM')) as min_d").collect()[0]["min_d"]
    # max_date_budget = budget_df.selectExpr("max(to_date(Period, 'yyyy-MM')) as max_d").collect()[0]["max_d"]

    # A more robust way for date range might be needed if budget dates are outside transaction dates
    # Or if you want to cover a fixed range like '2020-01-01' to '2025-12-31'
    date_range_df = spark.sql(f"SELECT sequence(to_date('{min_date_trans}'), to_date('{max_date_trans}'), interval 1 day) as date_array")
    dates_df = date_range_df.selectExpr("explode(date_array) as FullDate")

    dim_date_df = dates_df \
        .withColumn("DateKey", date_format(col("FullDate"), "yyyyMMdd").cast(IntegerType())) \
        .withColumn("Year", year(col("FullDate")).cast(IntegerType())) \
        .withColumn("Quarter", quarter(col("FullDate")).cast(IntegerType())) \
        .withColumn("Month", month(col("FullDate")).cast(IntegerType())) \
        .withColumn("MonthName", date_format(col("FullDate"), "MMMM")) \
        .withColumn("DayOfMonth", dayofmonth(col("FullDate")).cast(IntegerType())) \
        .withColumn("DayOfWeekName", date_format(col("FullDate"), "EEEE")) \
        .withColumn("WeekOfYear", weekofyear(col("FullDate")).cast(IntegerType())) \
        .withColumn("IsWeekend", dayofweek(col("FullDate")).isin([1, 7])) \
        .select("DateKey", "FullDate", "Year", "Quarter", "Month", "MonthName", "DayOfMonth", "DayOfWeekName", "WeekOfYear", "IsWeekend")
    dim_date_df.show(5)
    load_and_write_to_redshift(dim_date_df, "DimDate")

    # Create DimDepartment (from transactions for simplicity, real-world would be richer)
    # In real scenario, this would come from a master data source or be more complex
    dim_department_df = transactions_df.select("DepartmentID").distinct() \
        .withColumn("DepartmentKey", monotonically_increasing_id().cast(IntegerType())) \
        .withColumnRenamed("DepartmentID", "DepartmentID_NK")  # NK for Natural Key
        .withColumn("DepartmentName", col("DepartmentID_NK")) # Placeholder name
        .select("DepartmentKey", col("DepartmentID_NK").alias("DepartmentID"), "DepartmentName") # Rename back for consistency
    dim_department_df.show(5)
    load_and_write_to_redshift(dim_department_df, "DimDepartment")

    # Create DimAccount (from transactions)
    dim_account_df = transactions_df.select("AccountID").distinct() \
        .withColumn("AccountKey", monotonically_increasing_id().cast(IntegerType())) \
        .withColumnRenamed("AccountID", "AccountID_NK")
        .withColumn("AccountName", col("AccountID_NK")) # Placeholder name
        .withColumn("AccountType", lit("Unknown")) # Placeholder
        .select("AccountKey", col("AccountID_NK").alias("AccountID"), "AccountName", "AccountType")
    dim_account_df.show(5)
    load_and_write_to_redshift(dim_account_df, "DimAccount")

    # Create DimScenario
    scenarios = [('Actual', 1), ('Budget', 2)]
    dim_scenario_df = spark.createDataFrame(scenarios, ["ScenarioName", "ScenarioKey"])
    dim_scenario_df.show()
    load_and_write_to_redshift(dim_scenario_df, "DimScenario")

    # --- 3. Fact Table Creation ---
    logger.info("Creating FactFinancials table...")

    # Prepare transactions data for fact table
    fact_trans_df = transactions_df \
        .withColumn("Date", to_date(col("Date"), 'yyyy-MM-dd')) \
        .withColumn("DateKey", date_format(col("Date"), "yyyyMMdd").cast(IntegerType())) \
        .withColumn("Amount", col("Amount").cast(DecimalType(18, 2)))

    # Join with dimensions to get surrogate keys
    fact_trans_df = fact_trans_df \
        .join(dim_department_df, fact_trans_df.DepartmentID == dim_department_df.DepartmentID, "left_outer") \
        .select(fact_trans_df["*"] , dim_department_df["DepartmentKey"].alias("DeptKey")) \
        .join(dim_account_df, fact_trans_df.AccountID == dim_account_df.AccountID, "left_outer") \
        .select(fact_trans_df["*"] , dim_account_df["AccountKey"].alias("AccKey"), col("DeptKey")) \
        .join(dim_scenario_df.where(col("ScenarioName") == 'Actual'), lit(True), "cross") \
        .select(
            col("TransactionID"),
            col("DateKey"),
            col("DeptKey").alias("DepartmentKey"),
            col("AccKey").alias("AccountKey"),
            dim_scenario_df["ScenarioKey"],
            col("Amount"),
            col("Date").alias("TransactionDate")
        )
    fact_trans_df = fact_trans_df.withColumn("BudgetAmount", lit(None).cast(DecimalType(18,2)))

    # Prepare budget data for fact table (simplified, assumes monthly budget)
    # More complex logic needed for period mapping (e.g. yyyy-MM to multiple DateKeys)
    budget_df = budget_df \
        .withColumn("Period_Date", to_date(col("Period"), 'yyyy-MM')) \
        .withColumn("BudgetAmount", col("BudgetAmount").cast(DecimalType(18, 2)))

    # This join for budget DateKey is simplistic. A real scenario might explode budget across all days of the month
    # or aggregate transactions to month for budget comparison.
    # For this PoC, we'll assume budget can be joined at a placeholder DateKey or needs a different grain.
    # Let's assume for now we are creating separate records for budget.
    fact_budget_df = budget_df \
        .join(dim_department_df, budget_df.DepartmentID == dim_department_df.DepartmentID, "left_outer") \
        .select(budget_df["*"] , dim_department_df["DepartmentKey"].alias("DeptKey")) \
        .join(dim_account_df, budget_df.AccountID == dim_account_df.AccountID, "left_outer") \
        .select(budget_df["*"] , dim_account_df["AccountKey"].alias("AccKey"), col("DeptKey")) \
        .join(dim_scenario_df.where(col("ScenarioName") == 'Budget'), lit(True), "cross") \
        .join(dim_date_df, date_format(col("Period_Date"), "yyyyMM") == date_format(dim_date_df["FullDate"], "yyyyMM"), "left_outer") \
        .select(
            col("BudgetID").alias("TransactionID"), # Using BudgetID as a form of transaction ID for budget records
            dim_date_df["DateKey"], # This will create budget rows for each day in the month. Consider if this is the desired grain.
            col("DeptKey").alias("DepartmentKey"),
            col("AccKey").alias("AccountKey"),
            dim_scenario_df["ScenarioKey"],
            lit(None).cast(DecimalType(18,2)).alias("Amount"),
            col("BudgetAmount"),
            col("Period_Date").alias("TransactionDate")
        ).distinct() # Distinct because of the date join potentially creating duplicates if not careful

    # Union actuals and budget (or handle them separately if preferred grain is different)
    # For this PoC, we will try to union them, but be aware of grain differences.
    # A more robust model might have FactActuals and FactBudget tables or a more complex union.
    # This union will have NULLs for Amount in budget rows and BudgetAmount in actual rows.
    # The current budget to day-level join is problematic for direct union if budget is monthly.
    # A better approach for budget might be to load it to a separate staging table
    # or aggregate actuals to monthly to join with monthly budget.

    # For simplicity of this PoC, let's focus on loading transactions as FactFinancials (actuals)
    # and acknowledge budget loading requires more thought on grain alignment.

    fact_financials_df = fact_trans_df \
        .withColumn("VarianceAmount", col("Amount") - col("BudgetAmount")) # This will be null if BudgetAmount is null
        .select(
            "TransactionID", "DateKey", "DepartmentKey", "AccountKey", "ScenarioKey",
            "Amount", "BudgetAmount", "VarianceAmount", "TransactionDate"
        )

    fact_financials_df.printSchema()
    fact_financials_df.show(10, truncate=False)

    load_and_write_to_redshift(fact_financials_df, "FactFinancials")

    logger.info("ETL Job Completed Successfully.")

except Exception as e:
    logger.error(f"Error during ETL job: {str(e)}")
    # Potentially send SNS notification on failure here
    raise e
finally:
    job.commit()
