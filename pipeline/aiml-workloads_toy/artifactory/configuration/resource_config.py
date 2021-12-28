import os
import boto3
from artifactory.configuration.base_config import BaseConfig
from artifactory.configuration.commons import init_logger

class Configuration(BaseConfig):

    def __init__(self, log_level=None, ssm_interface=None):
        """
        Complementary Data Lake Configuration config stores the Data Lake specific parameters
        :param log_level: level the class logger should log at
        :param ssm_interface: ssm interface, normally boto, to read parameters from parameter store
        """
        self.log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
        self._logger = init_logger(__name__, self.log_level)
        self._ssm = ssm_interface or boto3.client('ssm')        
        super().__init__(self.log_level, self._ssm)
        self._fetch_from_ssm()

    def _fetch_from_ssm(self):
        self._region = None
        self._environment=None
        self._artifacts_bucket = None
        self._segments_bucket = None
        self._data_preparation_bucket = None
        self._sns_segments_topic_arn = None
        self._sns_data_preparation_topic_arn = None
        self._aiml_segments_database=None
        self._aggregated_transactions_table = None
        self._emission_table = None
        self._redemption_table = None
        self._rules_table = None
        self._aiml_data_database=None
        self._registered_sales_table = None
        self._analytics_database = None
        self._gigigo_database = None
        self._kms_key_id=None
        self._lambda_iam_role = None
        self._glue_iam_role = None
        self._step_functions_iam_role = None
        self._sagemaker_iam_role = None

    @property
    def region(self):
        if not self._region:
            self._logger.info("Getting Region from SSM")
            self._region = self._get_ssm_param(
                '/AIML/Foundations/Commons/Region')
        else:
            self._logger.info("Region from DataLakeConfiguration Instance")
        return self._region

    @property
    def environment(self):
        if not self._environment:
            self._logger.info("Getting Environment from SSM")
            self._environment = self._get_ssm_param(
                '/AIML/Foundations/Commons/Environment')
        else:
            self._logger.info("Environment from DataLakeConfiguration Instance")
        return self._environment

    @property
    def segments_bucket(self):
        if not self._segments_bucket:
            self._logger.info("Getting Segments bucket name from SSM")
            self._segments_bucket = self._get_ssm_param(
                '/AIML/Foundations/S3/SegmentsBucketName')
        else:
            self._logger.info("Segments bucket from DataLakeConfiguration Instance")
        return self._segments_bucket

    @property
    def data_preparation_bucket(self):
        if not self._data_preparation_bucket:
            self._logger.info("Getting Data preparation bucket from SSM")
            self._data_preparation_bucket = self._get_ssm_param(
                '/AIML/Foundations/S3/DataBucketName')
        else:
            self._logger.info("Data bucket name from DataLakeConfiguration Instance")
        return self._data_preparation_bucket

    @property
    def sns_segments_topic_arn(self):
        if not self._sns_segments_topic_arn:
            self._logger.info("Getting Segments Topic SNS from SSM")
            self._sns_segments_topic_arn = self._get_ssm_param(
                '/AIML/Foundations/SNS/SegmentsNotificationsTopicArn')
        else:
            self._logger.info("Segments Topic SNS from DataLakeConfiguration Instance")
        return self._sns_segments_topic_arn

    @property
    def sns_data_preparation_topic_arn(self):
        if not self._sns_data_preparation_topic_arn:
            self._logger.info("Getting Data preparation Topic SNS from SSM")
            self._sns_data_preparation_topic_arn = self._get_ssm_param(
                '/AIML/Foundations/SNS/DataNotificationsTopicArn')
        else:
            self._logger.info("Data Preparation Topic SNS from DataLakeConfiguration Instance")
        return self._sns_data_preparation_topic_arn

    @property
    def aiml_segments_database(self):
        if not self._aiml_segments_database:
            self._logger.info("Getting Segments database from SSM")
            self._aiml_segments_database = self._get_ssm_param(
                '/AIML/Foundations/Glue/SegmentsDatabaseName')
        else:
            self._logger.info("Segments database from DataLakeConfiguration Instance")
        return self._aiml_segments_database

    @property
    def aggregated_transactions_table(self):
        if not self._aggregated_transactions_table:
            self._logger.info("Getting aggregated transactions table from SSM")
            self._aggregated_transactions_table = self._get_ssm_param(
                '/AIML/Foundations/Glue/AggregatedTransactionsTable')
        else:
            self._logger.info("Aggregated transactions table from DataLakeConfiguration Instance")
        return self._aggregated_transactions_table

    @property
    def emission_table(self):
        if not self._emission_table:
            self._logger.info("Getting emission table from SSM")
            self._emission_table = self._get_ssm_param(
                '/AIML/Foundations/Glue/EmissionSegmentationTable')
        else:
            self._logger.info("Emission table from DataLakeConfiguration Instance")
        return self._emission_table

    @property
    def redemption_table(self):
        if not self._redemption_table:
            self._logger.info("Getting redemption table from SSM")
            self._redemption_table = self._get_ssm_param(
                '/AIML/Foundations/Glue/RedemptionSegmentationTable')
        else:
            self._logger.info("Redemption table from DataLakeConfiguration Instance")
        return self._redemption_table

    @property
    def rules_table(self):
        if not self._rules_table:
            self._logger.info("Getting rules table from SSM")
            self._rules_table = self._get_ssm_param(
                '/AIML/Foundations/Glue/RuleSegmentationTable')
        else:
            self._logger.info("Rules table from DataLakeConfiguration Instance")
        return self._rules_table

    @property
    def aiml_data_database(self):
        if not self._aiml_data_database:
            self._logger.info("Getting AIML data database from SSM")
            self._aiml_data_database = self._get_ssm_param(
                '/AIML/Foundations/Glue/DataDatabaseName')
        else:
            self._logger.info("AIML Data Database from DataLakeConfiguration Instance")
        return self._aiml_data_database

    @property
    def registered_sales_table(self):
        if not self._registered_sales_table:
            self._logger.info("Getting AIML registered sales table from SSM")
            self._registered_sales_table = self._get_ssm_param(
                '/AIML/Foundations/Glue/RegisteredSalesProcessedTable')
        else:
            self._logger.info("AIML registered sales table from DataLakeConfiguration Instance")
        return self._registered_sales_table

    @property
    def analytics_database(self):
        if not self._analytics_database:
            self._logger.info("Getting Analytics Database from SSM")
            self._analytics_database = self._get_ssm_param(
                '/AIML/Foundations/Glue/AnalyticsDatabaseName')
        else:
            self._logger.info("Analytics database from DataLakeConfiguration Instance")
        return self._analytics_database

    @property
    def gigigo_database(self):
        if not self._gigigo_database:
            self._logger.info("Getting Gigigo Database from SSM")
            self._gigigo_database = self._get_ssm_param(
                '/AIML/Foundations/Glue/GigigoDatabaseName')
        else:
            self._logger.info("Gigigo database from DataLakeConfiguration Instance")
        return self._gigigo_database

    @property
    def kms_key_id(self):
        if not self._kms_key_id:
            self._logger.info("Getting KMS key ID from SSM")
            self._kms_key_id = self._get_ssm_param(
                '/AIML/Foundations/KMS/KeyID')
        else:
            self._logger.info("KMS key ID from DataLakeConfiguration Instance")
        return self._kms_key_id

    @property
    def lambda_iam_role(self):
        if not self._lambda_iam_role:
            self._logger.info("Getting Lambda IAM role key ID from SSM")
            self._lambda_iam_role = self._get_ssm_param(
                '/AIML/Foundations/IAM/LambdaRoleArn')
        else:
            self._logger.info("Lambda IAM role from DataLakeConfiguration Instance")
        return self._lambda_iam_role

    @property
    def glue_iam_role(self):
        if not self._glue_iam_role:
            self._logger.info("Getting Glue Role from SSM")
            self._glue_iam_role = self._get_ssm_param(
                '/AIML/Foundations/IAM/GlueRoleArn')
        else:
            self._logger.info("Getting Glue Role from DataLakeConfiguration Instance")
        return self._glue_iam_role

    @property
    def step_functions_iam_role(self):
        if not self._step_functions_iam_role:
            self._logger.info("Getting Step Functions Role from SSM")
            self._step_functions_iam_role = self._get_ssm_param(
                '/AIML/Foundations/IAM/StepFunctionsRoleArn')
        else:
            self._logger.info("Getting Step Functions Role from DataLakeConfiguration Instance")
        return self._step_functions_iam_role

    @property
    def sagemaker_iam_role(self):
        if not self._sagemaker_iam_role:
            self._logger.info("Getting SageMaker Role from SSM")
            self._sagemaker_iam_role = self._get_ssm_param(
                '/AIML/Foundations/IAM/SageMakerRoleArn')
        else:
            self._logger.info("Getting SageMaker Role from DataLakeConfiguration Instance")
        return self._sagemaker_iam_role

