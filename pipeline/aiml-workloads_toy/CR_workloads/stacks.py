import os
import ast
import json
import boto3
import sys
import threading
from aws_cdk import aws_glue as glue
from aws_cdk import core as cdk
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from aws_cdk import aws_ssm as ssm
from aws_cdk import aws_sagemaker
from typing import Any, Dict, List, Optional, Sequence, Union
from aws_cdk import aws_lambda, aws_iam as iam, aws_events as events
from artifactory.configuration.resource_config import Configuration
from CR_workloads.configuration.constants import ArtifactoryConstants
from StackConstructor.stackconstructor import AWSStackConstructor

class CRStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, logger, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


class CRFE(CRStack,AWSStackConstructor):
    def __init__(self, scope: cdk.Construct, logger, config: Configuration, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, logger)

        logger.info(f"\n************************************************************************************************************************\n******************************{construct_id.rjust((60-len(construct_id))//2+len(construct_id)).ljust(60)}******************************\n************************************************************************************************************************")
        ###########################################################################
        # step_01. creation SSM parameters (if exists).
        ###########################################################################
        super().ssm_constructor(config,ArtifactoryConstants)
        ###########################################################################
        # step_02. Creacion de layers. Heredo el metodo desde ArcosMtkConstructor.
        ###########################################################################
        #layers = super().layers_constructor(config,ArtifactoryConstants,construct_id)
        ###########################################################################
        # step_03. Creacion de lambdas. Agrego layers a todas las funciones.
        ###########################################################################
        #env_vars_lambdas = {'SEGMENTS_BUCKET': config.segments_bucket,
        #                               'AIML_SEGMENTS_DATABASE': config.aiml_segments_database,
        #                               'AIML_DATA_DATABASE': config.aiml_data_database,
        #                               'GIGIGO_DATABASE': config.gigigo_database,
        #                               'REGISTERED_SALES_TABLE': config.registered_sales_table,
        #                               'KMS_KEY_ID': config.kms_key_id,
        #           }
        #lambdas = super().lambda_constructor(config,ArtifactoryConstants.LAMBDA_HANDLER_PATH,construct_id,env_vars_lambdas,layers)
        ###########################################################################
        # step_04. Creacion de glue jobs. Agrego layers a todas las funciones.
        ###########################################################################
        glues = super().glue_constructor(config,ArtifactoryConstants,construct_id,config.segments_bucket)
        ###########################################################################
        # step_05. Creacion de Maquina de estados.
        ###########################################################################
        # diccionario para mapear los strings en la maquina de estados.
        map_dict = {"sns_arn": config.sns_segments_topic_arn}
        # defino la maquina de estados.
        state_machine = super().state_machine_constructor(config,ArtifactoryConstants,construct_id,map_dict)
        ###########################################################################
        # step_06. Creacion Lamba de ruteo.
        ###########################################################################
        env_vars_routing = {
                    'KMS_KEY_ID': config.kms_key_id,
                    'STATE_MACHINE':state_machine.attr_arn
                } 
        routing = super().lambda_constructor(config,ArtifactoryConstants.LAMBDA_ROUTING,construct_id,env_vars_routing)
        ###########################################################################
        # step_07. Creacion de Cron
        ###########################################################################
        #super().scheduled_event_constructor(config,ArtifactoryConstants,construct_id,routing['aiml-dev-recsys_Lambda_lambda_routing'].function_arn\
        #        ,'aiml-dev-recsys_Lambda_lambda_routing')

