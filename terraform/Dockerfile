FROM hashicorp/terraform:latest

ARG GCP_PROJECT_NAME
ARG GCP_LOCATION
ARG ARTIFACT_STORAGE
ARG GOOGLE_CREDENTIALS
COPY /terraform/function_source/* /app/function_source/
COPY /terraform/*.tf /app/
COPY ${GOOGLE_CREDENTIALS} /app/
COPY /terraform/*.json /app/

#ARG varlist="-var credentials=${GOOGLE_CREDENTIALS} -var project=${GCP_PROJECT_NAME} -var region=${DEFAULT_GCP_REGION} -var location=${GCP_LOCATION} -var bq_dataset_name=${BQ_DATASET_NAME}"
ARG varfile="credentials=\"${GOOGLE_CREDENTIALS}\" \nproject=\"${GCP_PROJECT_NAME}\" \nlocation=\"${GCP_LOCATION}\"\ngcs_bucket_name=\"${ARTIFACT_STORAGE}\""
WORKDIR /app/
RUN echo -e ${varfile} > varfile.tfvars
RUN terraform init 
RUN terraform plan -var-file varfile.tfvars 
RUN terraform apply -var-file varfile.tfvars -auto-approve