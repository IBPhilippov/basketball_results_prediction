FROM python:3.9
ARG GOOGLE_CREDENTIALS


#EXPOSE 5000


RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-cli -y

COPY ${GOOGLE_CREDENTIALS} ${GOOGLE_CREDENTIALS}
RUN gcloud auth login --cred-file=${GOOGLE_CREDENTIALS}
RUN pip install google-cloud-storage mlflow psycopg2-binary
ENV GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_CREDENTIALS}


