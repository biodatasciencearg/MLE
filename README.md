<div><img src="./img/logo.png" width="200px" align="right"></div>

<br>
<br><br><br><br>

# MLE_Challenge
Brief challenge to measure API and pipeline deployment as a Machine Learning Engineer


* The functional / technical specifications of the document ("./challenge/Machine_Learning_Engineer_Technical_Challenge_Kueski.docx") were followed for the implementation of the API.



### Feature engineering Pipeline.
#### 4.1. Understand the features (notebook 1)
The Data Scientist (DS) create 5 feature derived from original data as:

**nb_previous_loans**: number of loans granted to a given user, before the current loan.

**avg_amount_loans_previous**: average amount of loans granted to a user, before the current rating.

**age**: user age in years.

**years_on_the_job**: years the user has been in employment.

**flag_own_car**: flag that indicates if the user has his own car.



But he/she doesn't take into account several considerations as follows:

* **Age and years_on_the_job**  both variables are derived from date data type. Some records with dates after this century (e.g loan number 208089 with job_start_date 3021-09-18). Using to_datetime function from pandas ends in a overflow representation  on dates ( max Timestamp('2262-04-11 23:47:16.854775807')) given an Nan value instead. Pyspark does not have this issue and finally got a datetime value. So, to get a good quality check over the records I prefer just checking the data type and leave the QA  to the Transformer pipeline in the prediction layer. Another problem identified is the imputation methods. All the missing values are replaced by 0, this is incorrect for at least two reasons: change the estimator of the distribution and from a business point of view maybe is not the best representation for a missing value (e.g  I prefer replace missing values in "Age" column with the average value instead 0). Another problem could be dates before the current date. The DS never check that.

* **avg_amount_loans_previous** I proposed a different approach to compute this variable because use a  loop is an inefficient way to compute the values. Instead I prefer vectorization and windowing approach. The Imputation method seems to be correct.

* **flag_own_car** variable. The strategy proposed was to replace all missing values with zero. This strategy could be a good initial assumption, but we need to verify with  EDA.


#### 4.2. Build data pipelines to compute these features and train machine learning model (using notebook 2)
Opportunities for improvement found in notebook 2:

* Imputation methods and vectorization (discussed on 4.1)

* SMOTE before train / test split. This is incorrect because SMOTE tries to "balance" the original distribution with the idea of "show" to the model more instances for the minority class. So, I propose changing the order after train / test split. Also, this schema could affect the informed metrics.

* Training set. During notebook2 I thought that the best choice would be eliminate all the pseudoreplicates. In the current implementation feeds the model with all rows and you need to keep just the last subset of variables for each client.

* Don't Include client Id during training. Also could be problematic because you don't need to feed the algorithm with ids (information leakage) Because random forest could find the right partition over the id space and as result improve artificially the metrics


As a results I builded a stack to be deployed with cdk that include a state machine triggered by a cron.
The repository you can find in "pipeline/aiml-workloads_toy/". Each Folder controls services as Glue, State machine, lambdas through json file in each environment. The proposed state machine is depicted as follows:





<div><img src="./img/state_machine.png" width="400px" align="right"></div>
<br>
<br><br><br><br>

**"CreditRiskFE"** reference to a ETL glue job (./pipeline/aiml-workloads_toy/CR_workloads/Glue/Jobs/step_01_fe) wroted in pyspark derived from notebook1 (jupyter notebook version on notebooks/01.Features_engineering.ipynb)


**"Backtesting"** right now is just a scaffold to in a future write a function that evaluates the performance of the current model and derivated metrics as auc, recall, f1, precision, etc. But in the credit risk score, I suggest KS (Kolmogorov-Smirnov) score and performance tables partitioned by deciles.


**"CRTrainingJob"** Right now Also is empty, but you can take the workflow on notebooks/02.Model_training.ipynb and adapt the pipeline to a pyspark script or develop a sagemaker processing job and do the transformation using a batch transform. The Goal of that training job is to make a new model,  triggered by a poor performance over the last records (denoting degradation of models). In the SSM parameters folder I setup a variable "DaysOW" to define observation and collect period (Figure below)


<br>
<br><br>
<div><img src="./img/ow.jpg" width="400px" align="left"></div>
<br>
<br><br><br><br>

### API Dev
Among the functional requirements is the creation/development of two APIs.
* (1) creating an API to serve  features for each client
* (2) creating a prediction service that uses the created features.

The Dockerfile is available to buil a container with all requirements.
If you run locally without a docker container you must to define enviroment variables (linux):
#### path to the last model. In production you could have multiple models in s3 and point to active model.
export KUESKI_MODEL_PATH="./model_risk.joblib"
##### url to api to get the features. In a real world you point to a aws endpoint.
export KUESKI_FEATURE_STORE_API_URL="http://localhost:8000"
#### path to feature store "online". In a real world scenario the query will be through a sql connector.
export KUESKI_FEATURE_STORE_PATH="sqlite:///feature_store_online.db"


Documentation is available at local host on **http://127.0.0.1:8000/docs**.

<div><img src="./img/documentation.png" width="500px" align="left"></div>
<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>


#### 4.3. Create an API to serve the features **http://127.0.0.1:8000/online_feature_store/client_id={id}**

A local API was developed as a Demo using FastAPI. The API interacts with a SQL database (this could be change in a real scenario to a SQL or NoSQL database as Aurora or DynamoDB) and serve the features as a json.

Some aspects that were taken into account that should be important to highlight:

* Check if the user exists on database.
* Architecture is compatible with a service with a subsecond time response.

<div><img src="./img/online_feature_store.png" width="700px" align="left"></div>
<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>

<div style="padding: 15px; border: 1px solid transparent; border-color: transparent; margin-bottom: 20px; border-radius: 4px; color: #3c763d; background-color: #dff0d8; border-color: #d6e9c6;">
In the real world, I would choose a storage infrastructure known as an "online" feature store, that presents a low latency appropriate for a service that should respond in milliseconds. For this reason, I prefer SQL or Dynamodb databases and it would avoid store features on parquet and avro files.
</div>


##### 4.4. Create an API to make predictions  **http://127.0.0.1:8000/credit_risk/client_id={id}**
To develop the second API also was used FastAPI. This API gets the features from the first API and returns each feature given a user/client id, the probability/score of "Credit Risk Default" and the associated label.

<div><img src="./img/credit_risk.png" width="700px" align="left"></div>
<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
You can test directly on docs web page:
<div><img src="./img/e_credit_risk.png" width="700px" align="left"></div>
<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>

The important aspects to pointing out could be:

* QA over each characteristic building a pandera model to be sure about the data type and the imputation of each variable. In fact, I return an field with all columns with qa problems ("qa_failure_cases") and also print by console to be capture by for example "CloudWatch logs".



## Final remarks:

#### API
In a real-world scenario ( and with a considerable more amount of time) the deployment for APIs alternate (volume dependency) between fastAPI with lambda functions behind an api gateway with load balancers (scalable solutions) or an EC2 with a docker image of the APIs the actual technical specification includes just the development of a local API. Other stuffs to be considered as security/governance:
*  Create users and tokens to consume the API services. 

*  Library to encrypt data (sensible data for clients)

*  Write headers and records for any API call to identify consume patters or DNS attacks.

#### FE
For the feature engineering process. We will choose between SQL and NoSQL databases to create the feature store. Also, I will create a backtesting step to control the degradation of the models with an SNS step when the models drop from pre-established thresholds. Also, work about the standardization of sklearn transformers and/or include Pandera with Fouge in the pyspark preprocessing steps. The QA over features needs a to be improved and make better handling during first step of feature enginnering process. I'd like to be more time to developed the re-train process (**"CRTrainingJob"** Figure state machine) just I could only develop  the notebooks with transformers. 

#### CI/CD
**IMPORTANT** repository implementation (pipeline / aiml-workloads_toy) is only possible if you have all configuration in aws (glue, lambda, step functions policy, permissions, etc.). In my account, I implemented all artifacts/resources. I am sending you only for a demonstration purpose that I have been capable of. To finish I need to develop the final step of a CI/CD, using cdk pipeline to define account (prod/dev) unitary test, etc.


<div><img src="./img/cdk_resource_print.png" width="1000px" align="left"></div>
