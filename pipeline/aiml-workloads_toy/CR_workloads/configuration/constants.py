#######################################################
# Author: cgg
#######################################################
import os


# PATH BASE: "/Users/gocamilo/Documents/projects/AR-arcos/codecommit/common-artifactory/artifactory"
class ArtifactoryConstants:

    # others
    SAGEMAKER = "emr/artifacts/scripts"

    # CloudWatch constants
    BASE_PATH = os.getcwd()
    SUBPATH = "CR_workloads"
    GLUE_JOB_HANDLERS_S3_PREFIX = "artifacts/code/"
    GLUE_JOB_HANDLERS_PATH = f"{BASE_PATH}/{SUBPATH}/Glue/Jobs"
    CLOUDWATCH_SCHEDULED_EVENT_PATH = f"{BASE_PATH}/{SUBPATH}/CloudWatch/Events/ScheduledEvents/initialize_recommender_system_event"
    STATE_MACHINE_PATH = f"{BASE_PATH}/{SUBPATH}/StepFunctions/state_machine/"
    SSM_BASE_PATH=f"{BASE_PATH}/{SUBPATH}/SSM/Parameters"
    SSM_BASE_NAME="/AIMLtoy/Workloads/"
    LAMBDA_ROUTING     = f"{BASE_PATH}/{SUBPATH}/Routing/"
    LAMBDA_HANDLER_PATH= f"{BASE_PATH}/{SUBPATH}/Lambda/Functions/"
    LAYERS_PATH= f"{BASE_PATH}/{SUBPATH}/Layers/"
