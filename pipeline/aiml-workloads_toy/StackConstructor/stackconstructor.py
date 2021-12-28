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


class AWSStackConstructor():
    def __init__(self, config: Configuration, **kwargs) -> None:
        pass 

    def print_hello_world(self):
        print("hello World")

    def create_scheduled_event(self, event_name, target_arn, target_name,
                        data) -> events.CfnRule:

        schedule_expression = data["schedule_expression"]
        state = data["state"]
        description = data.get("description", "No description")
        lambda_permission_id = event_name + "permission"

        events_target_property = events.CfnRule.TargetProperty(
            id=target_name+'_property',
            arn=target_arn)

        event_template=events.CfnRule(self,
                       id=event_name,
                       name=event_name,
                       description=description,
                       schedule_expression=schedule_expression,
                       state=state,
                       targets=[events_target_property])

        aws_lambda.CfnPermission(self,
                                 id=lambda_permission_id,
                                 action="lambda:InvokeFunction",
                                 function_name=target_name,
                                 principal = "events.amazonaws.com",
                                 source_arn = event_template.attr_arn)

        return event_template

    def create_state_machine(self, states_name, states_definition, states_role_arn,
                             states_type="STANDARD") -> sfn.CfnStateMachine:
        states_template=sfn.CfnStateMachine(self,
                            id=states_name,
                            state_machine_name=states_name,
                            state_machine_type=states_type,
                            role_arn=states_role_arn,
                            definition_string=states_definition)
        return states_template

    def create_lambda_function(self, config: Configuration, lambda_function_name, script_location, data, environment_variables,layers=None) -> aws_lambda.CfnFunction:
        """Funcion que toma cmo argumento el json y crea la funcion lambda."""
        property_python_version = data['property_python_version']
        runtime=aws_lambda.Runtime(str(property_python_version))
        memory_size = data['memory_size']
        if "timeout" not in data:
            timeout_seconds = cdk.Duration.seconds(900)
        else:
            timeout_seconds = cdk.Duration.seconds(int(data['timeout']))
        #
        if layers is None:
            lambda_template = aws_lambda.Function(
                self,
                id=lambda_function_name,
                runtime=aws_lambda.Runtime(property_python_version),
                code=aws_lambda.Code.asset(script_location),
                handler='lambda_function.handler',
                function_name = lambda_function_name,
                memory_size= memory_size,
                timeout = timeout_seconds,
                role=iam.Role.from_role_arn(
                    self,
                    id=f'{lambda_function_name}_role',
                    role_arn=config.lambda_iam_role,
                ),
                environment=environment_variables
            )
        else:
            lambda_template = aws_lambda.Function(
                self,
                id=lambda_function_name,
                runtime=aws_lambda.Runtime(property_python_version),
                code=aws_lambda.Code.asset(script_location),
                handler='lambda_function.handler',
                function_name = lambda_function_name,
                memory_size= memory_size,
                timeout = timeout_seconds,
                role=iam.Role.from_role_arn(
                    self,
                    id=f'{lambda_function_name}_role',
                    role_arn=config.lambda_iam_role,
                ),
                layers = layers,
                environment=environment_variables
            )
        return lambda_template

    def create_ssm_parameter(self, parameter_name, data) -> ssm.CfnParameter:
        ssm_type = data["type"]
        value=data["value"]
        description = data["description"]
        ssm_template = ssm.CfnParameter(
            self,
            id=parameter_name,
            name=parameter_name,
            type=ssm_type,
            value=value,
            description=description
        )
        return ssm_template

    def create_glue_job(self, config: Configuration, glue_job_handler_name, script_location,
                        data, dependencies_location=None) -> glue.CfnJob:

        property_name = data['property_name']
        property_python_version = data['property_python_version']
        max_concurrent_runs = data['max_concurrent_runs']
        max_retries = data['max_retries']
        timeout = data['timeout']
        job_description = data.get("description", "No description")
        dependencies_path = {'--extra-py-files': dependencies_location} if dependencies_location is not None else {}
        default_arguments = ast.literal_eval(data.get("default_arguments", "{}"))
        default_arguments.update(dependencies_path)

        job_command_property = glue.CfnJob.JobCommandProperty(
            name=property_name,
            python_version=property_python_version,
            script_location=script_location
        )

        execution_property = glue.CfnJob.ExecutionPropertyProperty(
            max_concurrent_runs=max_concurrent_runs
        )

        if property_name == 'glueetl':
            worker_type = data['worker_type']
            number_of_workers = data['number_of_workers']
            glue_version = data['glue_version']

            glue_job_template = glue.CfnJob(
                self,
                glue_job_handler_name,
                command=job_command_property,
                role=config.glue_iam_role,
                description=job_description,
                execution_property=execution_property,
                glue_version=glue_version,
                max_retries=max_retries,
                name=glue_job_handler_name,
                default_arguments=default_arguments,
                number_of_workers=number_of_workers,
                timeout=timeout,
                worker_type=worker_type
            )

        elif property_name == 'pythonshell':
            max_capacity = data['max_capacity']

            glue_job_template = glue.CfnJob(
                self,
                glue_job_handler_name,
                command=job_command_property,
                role=config.glue_iam_role,
                description=job_description,
                execution_property=execution_property,
                max_capacity=max_capacity,
                max_retries=max_retries,
                name=glue_job_handler_name,
                default_arguments=default_arguments,
                timeout=timeout
            )

        else:
            print("Non valid glue job type")
            pass

        return glue_job_template

    def lambda_constructor(self,config,lambda_starting_path,construct_id,environment_variables,layers=None):
        """Funcion constructora de lambdas"""
        environment = config.environment
        lambda_jobs_dictionary = {}
        # navego sobre el arbol de directorios para encontrar definitions files.
        for dirpath, dirnames, files in os.walk(lambda_starting_path, topdown=False):
            for file_name in files:
                definition = f"{dirpath}/{file_name}"
                if f"definition-{environment}.json" in definition:
                    try:
                        # Loading and parsing "definition" file.
                        with open(definition, "rb") as f:
                            lambda_id = definition.split("/")[-2]
                            lambda_data = json.load(f)
                            lambda_handler_name   =   construct_id + "_Lambda_" +lambda_id
                            lambda_general_path   =   definition.replace(f"/definition-{environment}.json", "")
                            if layers is not None:
                                lambda_template = self.create_lambda_function(config, lambda_handler_name, lambda_general_path,
                                                              lambda_data, environment_variables,layers)
                            else:
                                lambda_template = self.create_lambda_function(config, lambda_handler_name, lambda_general_path,
                                                              lambda_data, environment_variables)
                            lambda_jobs_dictionary[lambda_handler_name]= lambda_template
                    except Exception as e:
                        print(e)
                        raise e
        return lambda_jobs_dictionary

    def ssm_constructor(self,config,ArtifactoryConstants):
        ssm_starting_path = ArtifactoryConstants.SSM_BASE_PATH
        ssm_base_path = ArtifactoryConstants.SSM_BASE_NAME
        #itero sobre los directorios.
        for dirpath, dirnames, files in os.walk(ssm_starting_path, topdown=False):
            for file_name in files:
                definition = f"{dirpath}/{file_name}"
                if f"definition-{config.environment}.json" in definition:
                    try:
                        with open(definition, "rb") as f:
                            parameter_id = definition.split("/")[-2]
                            parameter_category = definition.split("/")[-3]
                            data = json.load(f)
                            parameter_name = ssm_base_path + parameter_category + "/" + parameter_id
                            self.create_ssm_parameter(parameter_name, data)

                    except Exception as e:
                        print(e)
                        raise TypeError(e)

                else:
                    pass
    def layers_constructor(self,config,ArtifactoryConstants,construct_id,runtime='python3.7',build_from_scratch=True):
        """ Funcion que crea layers desde cero o permite tomar una existente https://github.com/keithrozario/Klayers"""
        import os
        import json
        environment = config.environment
        layers_lst  = []
        for dirpath, dirnames, files in os.walk(ArtifactoryConstants.LAYERS_PATH, topdown=False):
            for file_name in files:
                definition = f"{dirpath}/{file_name}"
                if f"definition-{environment}.json" in definition:
                    try:
                        print(definition)
                        with open(definition, "rb") as f:
                            parameter_id = definition.split("/")[-2]
                            parameter_category = definition.split("/")[-3]
                            data = json.load(f)
                            build_from_scratch=False
                    except:
                        print("Error loading json")
        # Si no tengo un definition creo las layers desde cero.
        if build_from_scratch:
            runtime=aws_lambda.Runtime(str(runtime))
            # listado de directorios donde habria una layer.
            layers_dirs = [d.name for d in os.scandir(ArtifactoryConstants.LAYERS_PATH) if d.is_dir()]
            # listado de layer que voy a exportar.
            # itero sobre los directorios que generan layers.
            for i,layer_dir in enumerate(layers_dirs):
                # Creo la layer.
                layer = aws_lambda.LayerVersion(self, id = '{}_Layer_{}'.format(construct_id,layer_dir), code = aws_lambda.AssetCode(ArtifactoryConstants.LAYERS_PATH + "/" + layer_dir + '/src/'), compatible_runtimes = [runtime])
                # la adiciono a una lista de layers de este recurso.
                layers_lst.append(layer)
        else:
            for i,arn_layer in enumerate(data['arn_layer_lst']):
                # Creo la layer.
                layer = aws_lambda.LayerVersion.from_layer_version_arn(self, f'{construct_id}_layercopy_{i}', f"{arn_layer}")
                # la adiciono a una lista de layers de este recurso.
                layers_lst.append(layer)
                # devuelvo el listado de layers.
        return layers_lst
    def glue_constructor(self,config,ArtifactoryConstants,construct_id,glue_artifactory_bucket):
        s3_client = boto3.client("s3")
        glue_artifactory_bucket = str(glue_artifactory_bucket)
        glue_starting_path = ArtifactoryConstants.GLUE_JOB_HANDLERS_PATH
        glue_jobs_dictionary={}
        environment = config.environment

        for dirpath, dirnames, files in os.walk(glue_starting_path, topdown=False):
            for file_name in files:
                definition = f"{dirpath}/{file_name}"
                if f"definition-{environment}.json" in definition:
                    try:
                        with open(definition, "rb") as f:
                            handler_category = definition.split("/")[-3]
                            handler_id = definition.split("/")[-2]
                            artifactory_key_suffix = handler_category + "/" + handler_id
                            glue_data = json.load(f)
                            job_handler_name = construct_id + "_" + handler_category + "_" + handler_id
                            main_script_path = definition.replace(f"definition-{environment}.json", "main.py")
                            main_script_key = ArtifactoryConstants.GLUE_JOB_HANDLERS_S3_PREFIX + \
                                              artifactory_key_suffix + "/main.py"

                            with open(main_script_path, "rb") as object_file:
                                s3_client.upload_fileobj(
                                    object_file, glue_artifactory_bucket, main_script_key, Callback=ProgressPercentage(main_script_path))
                                handler_script_location = "s3://" + glue_artifactory_bucket + "/" + main_script_key

                            dependencies_file = glue_data.get("dependencies_file", None)
                            handler_dependencies_location = None
                            if dependencies_file is not None:
                                dependencies_path = definition.replace(f"definition-{environment}.json", dependencies_file)
                                dependencies_key = ArtifactoryConstants.GLUE_JOB_HANDLERS_S3_PREFIX + \
                                                   artifactory_key_suffix + "/" + dependencies_file

                                with open(dependencies_path, "rb") as object_file:
                                    s3_client.upload_fileobj(
                                        object_file, glue_artifactory_bucket, dependencies_key,
                                        Callback=ProgressPercentage(dependencies_path))
                                    handler_dependencies_location = "s3://" + glue_artifactory_bucket + "/" + dependencies_key

                            glue_job = self.create_glue_job(config, job_handler_name, handler_script_location,
                                                 glue_data, handler_dependencies_location)
                            # cargo el glue a un diccionario.
                            glue_jobs_dictionary[job_handler_name] = glue_job

                    except Exception as e:
                        print(e)
                        raise TypeError(e)

                else:
                    pass
        return glue_jobs_dictionary

    def state_machine_constructor(self,config,ArtifactoryConstants,construct_id,map_dict):
        state_machine_starting_path = ArtifactoryConstants.STATE_MACHINE_PATH
        definition = f"{state_machine_starting_path}/main.json"
        try:
            with open(definition, "rb") as f:
                states_id = definition.split("/")[-2]
                states_definition = json.dumps((json.load(f))) % map_dict
                states_name=construct_id +'_StateMachine_'+ states_id
                states_role_arn=config.step_functions_iam_role
                state_machine_template=self.create_state_machine(states_name=states_name,
                                          states_definition=states_definition,
                                          states_role_arn=states_role_arn)
            return state_machine_template
        except Exception as e:
            print(e)
            raise TypeError(e)
    def scheduled_event_constructor(self,config,ArtifactoryConstants,construct_id,target_arn,target_name):
        cloudwatch_lambda_path = ArtifactoryConstants.CLOUDWATCH_SCHEDULED_EVENT_PATH
        event_definition = f"{cloudwatch_lambda_path}/definition-{config.environment}.json"
        try:
            with open(event_definition, "rb") as f:
                event_id = event_definition.split("/")[-2]
                event_data = json.load(f)
                event_name = construct_id + "_Event_" + event_id
                cloudwatch_template = self.create_scheduled_event(event_name=event_name,
                                                                  target_arn=target_arn,
                                                                  target_name=target_name,
                                                                  data=event_data)
        except Exception as e:
            print(e)
            raise e


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()
