# basketball_results_prediction
This repository contains the final project completed for the MLOps zoomcamp course, cohort 2024.

## Problem

This project is dedicated to the prediction of basketball games results basing of last match performances by to rival teams. This can be of interest by itsleft (for example, for those who are betting), but may also be used for detailed analysis: sport analysts, coaches and basketball players can use it to predict how team`s performance would be affected by changes in attacking precision, defending intensity, foul propensity and etc. 

---
## Data
The data for project is obtained from the NCAA (National Collegiate Athletic Association) public dataset in BigQuery. This dataset contains data about NCAA Basketball games, teams, and players, but in this project only games data is used. The scope of the analyzed games include team-level box scores from every NCAA men's basketball game from the 2013-14 season to the 2017-18 season. Used tables: bigquery-public-data.ncaa_basketball.mbb_teams_games_sr and  bigquery-public-data.ncaa_basketball.mbb_games. 

## Tools

1. Docker/Docker Compose for conteinerization and easy deployment.
2. Terraform for automated management of cloud infrastructure (IaC).
3. [Mage.AI](https://www.mage.ai) as an orchestrator.
4. MLflow for model tracking, experiements and model registry.
5. Google Cloud Storage (GCS) as a storage, Google BigQuery as data source.
   Google Cloud Storage is a Google Cloud Platform (GCP) alternative for S3 storage from Amazon Web Services (AWS).
7. Google Pub/Sub and Google Cloud Functions for deployment.
   Google Cloud PubSub is a fully-managed real-time messaging service, analogous to SQS/Kinesis in AWS.
   Google Cloud Functions is Google's serverless compute solution, equivalent to  Lambda in AWS.
9. [Evidently](https://www.evidentlyai.com) for monitoring.
10. Postgress as backend database.

In practice, you need to interact only with environment.env file, Mage.Ai and Google Cloud interface to prepare the account. Everything apart from it is deployed and managed automatically. 

   
---
## Requirements
1. Google Cloud Account with enabled billing (it will work with free 300$ quota for new users) and created service account with Owner rights ([instruction](https://docs.google.com/document/d/1gmRiIsNa_tk31YI5CB7p2V3m3N01sKAcD5FAVaQbwpg/edit?usp=sharing)).
2. Docker newer than v26.0 and docker-compose newer than v2.28.

## How to reproduce
0. Create Google Cloud Account and start free trial period. Google will give you 300$ free credit for 90 days that will cover expenses for testing this project (that will take 10$ from this quota at maximum). Enable Service Usage API and  (if you are logged in current browser, click [here](https://console.cloud.google.com/apis/api/serviceusage.googleapis.com/) and [here](https://console.cloud.google.com/apis/api/cloudresourcemanager.googleapis.com/), in opened tabs click _Enable_), create service account with Owner rights.  
1. Install Docker + Docker-Compose on your machine. If needed, follow installation instructions for your system from Docker`s [documentation](https://docs.docker.com/engine/install/).
2. Copy files from this repository or just clone it to your working directory using git.

   ```git clone https://github.com/IBPhilippov/basketball_results_prediction.git```
3. Move to the appeared directory, i.e.
   ```cd basketball_results_prediction```
4. Create a service account in Google Cloud Platform, grant it Admin/Editor access to your project, create json-key (if needed, follow the [instructions](https://cloud.google.com/iam/docs/keys-create-delete)) and upload json-file with keys to the directory basketball_results_prediction. Alternatively, you can just copy the content of json key downloaded from GCP, and paste it into the new file created by  ```nano credentials.json```

In any case, the json-key **must** be placed in the folder you downloaded from google. 

5. Change variables in environment.env accessing it in any convinient way. For example,
```nano environment.env```
Before you fill it
You need to insert your Google Cloud Platform project id after
```GCP_PROJECT_NAME=```
and the name of the file with json-keys after
```GOOGLE_CREDENTIALS=```
You can find GCP project in Google Cloud Console, for example here ![image](https://github.com/user-attachments/assets/b5bed20f-94e0-4f28-ab16-9a499ab87ec5) .
So, for my project it would be
```GCP_PROJECT_NAME=ibphilippov-mlops```


You can alter any variable here. Filled environment.env looks like this:
```
###Name of the file with credentials from service account###
GOOGLE_CREDENTIALS=credentials.json
###Id of your project###
GCP_PROJECT_NAME=my-project-id
###Location - do not alter if not needed###
GCP_LOCATION=US
###Name of bucket in Google Cloud Storage that will contain artifact data. Should be globally unique, choose some uncommon naming. You won`t interact with it manually, so meaningful name is not required###
ARTIFACT_STORAGE=my-artifact-storage
###Postgress Password###
DB_PASSWORD=example
DB_USER=postgress_user
DB_NAME=pgdata
```
6. Run the project with docker-compose.

   ```sudo docker compose --env-file=environment.env up```
OR
   ```sudo docker-compose --env-file=environment.env up```
depending on the way you installed docker-compose. You may also run it in detached mode, but it will be less convienient to track the process.

   ```sudo docker compose --env-file=environment.env up -d```
7. Wait some time. The commands in docker will automatically create all resourses and perform needed runs of data extraction pipeline and sklearn training pipeline.
It may take from 10 minutes up to an hour depending from your machine. For example, c2-standard-4 (4 vCPU, 2 core, 16 GB memory)  instance from Google Compute Engine will handle it in 15 minutes.
8. Check the pipeline status im MageAI UI (you can forward port 6789 and open http://localhost:6789/ in your browser, otherwise you need to connect to http://{your_machine_ip}:6789/. In UI you can observe that pipelines get_data_from_bq and train_sklearn were executed successfully.
9. Now you may send the data to the deployment module (serving at port 9696) via POST request and recieve the prediction in return. For example:
    ```
    curl -X POST http://0.0.0.0:9696/predict --header 'Content-Type: application/json' --json '[{"h_three_points_pct": 64.8,"h_three_points_att": 63.0, "h_two_points_pct": 41.0, "h_two_points_att": 39.0, "h_offensive_rebounds": 5.0, "h_defensive_rebounds": 30.0, "h_turnovers": 9.0,"h_steals": 0.0, "h_blocks": 4.0, "h_personal_fouls": 15.0, "h_points": 70.0, "a_three_points_pct": 41.7, "a_three_points_att": 12.0,"a_two_points_pct": 46.3, "a_two_points_att": 54.0, "a_offensive_rebounds": 5.0, "a_defensive_rebounds": 27.0, "a_turnovers": 20.0,"a_steals": 2.0,"a_blocks": 5.0, "a_personal_fouls": 5.0, "a_points": 99.0},{"h_three_points_pct": 64.8,"h_three_points_att": 23.0, "h_two_points_pct": 41.0, "h_two_points_att": 39.0, "h_offensive_rebounds": 5.0, "h_defensive_rebounds": 30.0, "h_turnovers": 9.0,"h_steals": 0.0, "h_blocks": 4.0, "h_personal_fouls": 15.0, "h_points": 70.0, "a_three_points_pct": 41.7, "a_three_points_att": 12.0,"a_two_points_pct": 46.3, "a_two_points_att": 54.0, "a_offensive_rebounds": 5.0, "a_defensive_rebounds": 27.0, "a_turnovers": 20.0,"a_steals": 2.0,"a_blocks": 5.0, "a_personal_fouls": 5.0, "a_points": 99.0}]'
   ```
returns
```
{"results":[-0.8319412738342693,3.353236690777813]}
```
    
10. If needed, you can connect to MLFlow (port 5000). Here you can see tracked experiments (1 ongoing by default named _basketball_), current prod model in model registry and results of model monitoring reports by Evidently (that are stored in experiment called _Model evaluation with Evidently_ (the idea to use MLFlow to monitor model performace and data drift taken from [Documentation by Evidently](https://docs.evidentlyai.com/integrations/evidently-and-mlflow). The latter will be created after some data will be sent to the deployment module (see previous (9) point).
11. If you need to automatically delete all GCP resources created by the project running, run
    ```sudo docker run terraform:Dockerfile destroy -var-file varfile.tfvars -auto-approve```

---

## What the code actually does
### TL;DR
Docker Compose creates Terraform, MLFlow, MageAI and a couple of auxillary containers and runs there some commands. **Using Terraform, it initializes all cloud infrastructure in GCP** (enables APIs, creates GCS buckets, Pub/Sub topics and subscriptions, a function in Google Cloud Functions). 
Using MageAI **as an orchestrator**, it runs a pipeline that gets data from NCAA database and uses it for training of the model. All training process inside MageAI **are tracked by MLFlow** that runs in a separate container and stores artifact data in GCS bucket, while keeping operational run/registry data in Postgress.
Once training is completed and prod model is stored in **model registry**, user may send data for obtaining new predictions. This is performed through a **python app in deployment container**. The app is triggering MageAI to send users' input to Cloud Functions via Pub/Sub, as well as a link to latest model's artifacts in GCS. Cloud Function uses this artifacts to recreate model, predict the target and send prediction back to MageAI and user. After returning prediction to a user, MageAI sends the data to the **monitoring pipeline**, where regression performance and data drift tests are executed. Their results are stored in MLFlow as a separate experiment. If tests results are unsatisfactory, the **retraining workflow** is triggered with newer data.


### Details
The main idea was to create end-to-end portable product that requires minimal adjustments in settings (here presented by environment.env), and can be run without manual interventions. Therfore, after initial setup everything runs automatically.

#### Containers
Docker Compose creates six containers: 
1. Container for Terraform.
2. Container for MLFlow.
3. Container for MageAI orchestrator.
4. Container for Python application on Flask for model deployment.
5. Container for Python application to trigger initial runs of MageAI pipelines.
6. Container for Postgress for backend.

#### Terraform
Terrafrom
   - using credentials file specified after **GOOGLE_CREDENTIALS** in environment.env, connects to a project specified after **GCP_PROJECT_NAME**.
   - enables in a project a number of API`s (full list in /terraform/variables.tf).
   - creates a bucket in a project specified after **GCP_PROJECT_NAME** in environment.env. The bucket is called after **ARTIFACT_STORAGE** in  environment.env.
   - creates two pub/sub topics: 1) _predictions-input_ and 2) _predictions-output_.
   - creates function _make_prediction_ in Google Cloud Functions. _make_prediction_ is triggered by any incoming messages in _predictions-input_ and runs a python script defined in /terraform/function_source/main.py. The result of this function is sent to _predictions-output_ topic and stored in **ARTIFACT_STORAGE** bucket.
#### MLFlow
Docker passes **GOOGLE_CREDENTIALS** in a container for MLFlow, so that MLFlow is connected to an **ARTIFACT_STORAGE** bucket for storing models` artifacts and to Postgress container to store run/operational data. User may reach MLFlow UI on port 5000, but the project workflow itself adresses it only from Mage.AI container. Both experiment tracking and model registry functionality are used. Apart from this, MLFlow is also used for model monitoring, storing runs of Evidently.AI reports.
#### MageAI
MageAI application is created from MageAI Docker image and four prepared pipelines inside a project named _Basketball_results_prediction_ stored in /Basketball_results_prediction/. Each pipeline contains API trigger that allows remote initiation of new pipeline runs with given parameters. This triggers are used to ensure the communication between pipelines.
1. _get_data_from_bq_ pipeline extracts data from ncaa_basketball public dataset in BigQuery. The connection between MageAI and GCP here (and everywhere else in this project) is made possible due to **GOOGLE_CREDENTIALS** that are passed from local folder to container during Docker Build process.
The SQL-query for data extraction:
```WITH previous_games as
  SELECT 
  team_id, 
  gametime, 
  game_id,
  LAG(three_points_pct) OVER team AS three_points_pct,
  LAG(three_points_att) OVER team AS three_points_att,
  LAG(two_points_pct) OVER team AS two_points_pct,
  LAG(two_points_att) OVER team AS two_points_att,
  LAG(offensive_rebounds) OVER team AS offensive_rebounds,
  LAG(defensive_rebounds) OVER team AS defensive_rebounds,
  LAG(turnovers) OVER team AS turnovers,
  LAG(steals) OVER team AS steals,
  LAG(blocks) OVER team AS blocks,
  LAG(personal_fouls) OVER team AS personal_fouls,
  LAG(points) OVER team AS points,
  LAG(gametime) OVER team AS gametime_lag,
  LAG(game_id) OVER team AS game_id_lag
  FROM bigquery-public-data.ncaa_basketball.mbb_teams_games_sr
  WHERE EXTRACT(year FROM gametime)={year} AND coverage='full'
  WINDOW team AS (PARTITION BY team_id ORDER BY gametime ASC))

SELECT
  games.game_id,
  pg_h.three_points_pct AS h_three_points_pct,
  pg_h.three_points_att AS h_three_points_att,
  pg_h.two_points_pct as h_two_points_pct,
  pg_h.two_points_att as h_two_points_att,
  pg_h.offensive_rebounds as h_offensive_rebounds,
  pg_h.defensive_rebounds as h_defensive_rebounds,
  pg_h.turnovers as h_turnovers,
  pg_h.steals as h_steals,
  pg_h.blocks as h_blocks,
  pg_h.personal_fouls as h_personal_fouls ,
  games.h_points as h_points,
  pg_a.three_points_pct as a_three_points_pct,
  pg_a.three_points_att as a_three_points_att,
  pg_a.two_points_pct as a_two_points_pct,
  pg_a.two_points_att as a_two_points_att,
  pg_a.offensive_rebounds as a_offensive_rebounds,
  pg_a.defensive_rebounds as a_defensive_rebounds,
  pg_a.turnovers as a_turnovers,
  pg_a.steals as a_steals,
  pg_a.blocks as a_blocks,
  pg_a.personal_fouls as a_personal_fouls,
  games.a_points as a_points
 
FROM
  bigquery-public-data.ncaa_basketball.mbb_games_sr games
  JOIN previous_games pg_h ON games.h_id=pg_h.team_id AND games.game_id=pg_h.game_id
  JOIN previous_games pg_a ON games.a_id=pg_a.team_id AND games.game_id=pg_a.game_id

WHERE
  EXTRACT(year FROM games.gametime)={year}
  AND pg_h.game_id_lag IS NOT NULL
  AND pg_a.game_id_lag IS NOT NULL
```

, here h-prefixed fields are game statistics parameters for the last game home team (except points that are for current games and essentialy form target for the model), a-prefixed fields are the same for away team, and **year** - is a parameter coming from the pipeline. Each pipeline run this query is excecuted twice for two different years: to obtain train and validation data. On the next step, the data is preprocessed in a way that pipeline separately returns train data features, validation data features, train data targets (h_paints - a_points), validation data targets and the metadata for pipeline run. After data preprocessing is over, the last block of this pipeline triggers the execution of the next pipeline.
2. _train_sklearn_ pipeline uses scikit-learn and hyperopt python libraries to tune ML model of different specifications and choose the one that shows best results on validation. Each tested model specification is logged in MLFlow with its metadata, performance metrics and artifacts. After all specifications with all examined set of hyperparameters are evaluated, the best performing model is put to model registry. 
3. _deployment_ pipeline is the only pipeline in this project that can`t be triggered inside the project (i.e. by other pipelines), but reacts to an external call. This call is managed by an application in container 4 and is triggered by user`s POST requests on port 9696. This pipeline puts incoming data  from POST request and location of the artifacts of the latest model from model registry to _predictions-input_ topic in Pub/Sub, where it immideately triggers the execution of _make_prediction_ in the Cloud Functions. The function will load the model from GCS using data from registry and apply it to make predictions from incoming data. If payload of the user`s request is correct (i.e. contains all fields - see query in the first pipeline), after the excecution of _make_prediction_ the models`  predictions will be returned to _predictions-output_ topic in Pub/Sub and saved in GCS. The message from Pub/Sub then will be passed to _monitoring_ pipeline, and the content of the file in GCS returned to user who initally sent request.
4. _monitoring_ pipeline runs regressions performance and data drift reports on grounds of Evidenlty. After each report run, it stores it`s result and metadata as an MLFlow-run in separate experiment. After all tests are done and their results logged, the pipeline checks wheter a data drift is detected or a significant decline in regression performance on a testing data with n>150 (i.e. it searches in a list of runs in experiment _Model evaluation with Evidently_ such run, where number of cases>150, either data drift is detected or significant reduction of predictive power is detected, and model`s metadata is equal to the one of prod model in model registry). If something is discovered, the retraining is called (i.e. _get_data_from_bq_ with updated parameters is triggered - and _train_sklearn_ consequently as well). 
#### Deployment
The python script in Docker runs using flask and unicorn serves at port 9696. It handles POST-requests with data point payloads and redirects them to the _deployment_ pipeline in MageAI. After pipeline is initiated, the script awaits it`s completion, and, reads results from GCS bucket, and returns it back to user.
#### Auxillary - Pipeline Initiation
The python script in Docker runs after MageAI container is started. It triggers first execution of _get_data_from_bq_ pipeline and waits 100 seconds before triggering _train_sklearn_ pipeline.





