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
2. Docker newer than v26.0> and docker-compose newer than v2.28.

## How to reproduce
0. Create Google Cloud Account and start free trial period. Google will give you 300$ free credit for 90 days that will cover expenses for testing this project (that will take 10$ from this quota at maximum). Enable Service Usage API and  (if you are logged in current browser, click [here](https://console.cloud.google.com/apis/api/serviceusage.googleapis.com/ and [here](https://console.cloud.google.com/apis/api/cloudresourcemanager.googleapis.com/), in opened tabs click _Enable_), create service account with Owner rights.  
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
GOOGLE_CREDENTIALS=creds.json
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
15. If you need to automatically delete all GCP resources created by the project running, run
    ```sudo docker run terraform:Dockerfile destroy -var-file varfile.tfvars -auto-approve```

---

## What the code actually does
### TL;DR
Docker Compose creates Terraform and MageAi containers and runs there some commands. Using Terraform, it creates a bucket in Google Cloud Storage, a dataset and a table inside it in BigQuery. Using Mage, it runs a pipeline that gets data from GDELT database, stores it into a bucket created by Terraform, and then uses Spark to aggregate data from the bucket and then load it into BigQuery table. 

### Details
0. The main idea was to create end-to-end portable product that requires minimal adjustments in settings (here presented by environment.env), and can be run without manual interventions. Therfore, after initial setup everything runs automatically.
1. When you run  ```sudo docker compose --env-file=environment.env up```, docker builds and runs two docker images: Terraform image and MageAI image. 
2. Terrafrom
   - creates a bucket on a project specified in environment.env after **GCP_PROJECT_NAME**. The bucket is called as a concatenation of GCP_PROJECT_NAME, BQ_DATASET_NAME and ADDITIONAL_PART specified in  environment.env. The bucket name is complex due to the requirements of uniqueness across GCP. If you face with error, indicating that such bucket already exists, please change ADDITIONAL_PART (any combination of letters and numbers will work).
   - creates a datased called **BQ_DATASET_NAME** . The dataset should be non-existing before run, otherwise and error will be raised.
   - creates a table **BQ_DATASET_NAME.events** partitioned by _DateEvent_ and clustered by _Year_ and _Event_. The field _Year_ will be used below to delete and upload data, the field _Event_  will be used to group data in groups for dashboard representation.
The operations performed by Terraform are defined in /terraform/Dockerfile
4. Mage.AI creates a project called _gdelt_cooperation_ and pipeline called _gdelt_spark_. It runs the pipeline five times ranging the _year_ variable from 2019 to 2024, and creates a trigger that will run pipeline on hourly basis (with _year_ =2024).
5. During each run, the pipeline
  - recieves data from public GDELT-database in BQ using the query
``` SELECT DISTINCT GLOBALEVENTID, _PARTITIONTIME as EventTimestamp, MonthYear, Year, EventCode, Actor1CountryCode, Actor2CountryCode, Actor1Type1Code, Actor2Type1Code 
      FROM `gdelt-bq.gdeltv2.events_partitioned`
      WHERE EXTRACT(YEAR FROM (TIMESTAMP_TRUNC(_PARTITIONTIME, DAY))) = {year}
      and EventRootCode='06' ###06 is a root code for material cooperation events
      and IsRootEvent=1 ###we need only root events, not followups or discussion
      and IFNULL(Actor1CountryCode,'')!=IFNULL(Actor2CountryCode,'') ###the interactions should be international
```
   - ingests data into a bucket in data lake created by terraform
   - reads data from bucket, initiates the spark session
   - gets the dictionaries of codes from GDELT-project site using requests-module.
   - using Spark, joins dictionaries with the data on events, and then aggregates data, counting number of unique events per each type, each actor couple, each county per day.
   - inserts aggregated data into table **GCP_PROJECT_NAME.BQ_DATASET_NAME.events** in BigQuery.
   
The pipeline is run from docker-compose command instruction. Preparation of Mage image to use Spark is defined in /mage/Dockerfile.
The mage project code is stored in /gdelt_cooperation/. 


