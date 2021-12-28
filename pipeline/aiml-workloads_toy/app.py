#!/usr/bin/env python3
import datetime
import json
import boto3
from aws_cdk                                          import core
from artifactory.configuration.commons                import init_logger
from artifactory.configuration.resource_config        import Configuration
from CR_workloads.stacks                              import CRFE

ssm = boto3.client('ssm')

# Load environment parameters
logger = init_logger(__name__, "INFO")
config = Configuration()
environment = config.environment
print(environment)

app = core.App()
# levanto todas las lambdas, layers etc que van a ser comunes a todos los repos.
stack_name =  "aimltoy-" + environment + "CRFE"
cr_stack      = CRFE(app, logger, config,stack_name)

app.synth()
print("Successfully ended at %s" % datetime.datetime.now())
