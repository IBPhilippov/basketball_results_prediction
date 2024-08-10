FROM python:3.9-slim

ARG ARTIFACT_STORAGE
ARG GOOGLE_CREDENTIALS
ENV ARTIFACT_STORAGE=${ARTIFACT_STORAGE}

COPY ${GOOGLE_CREDENTIALS} app/credentials.json
COPY /deployment/* app/
WORKDIR /app 
RUN pip3 install -r requirements.txt

EXPOSE 9696 

ENTRYPOINT gunicorn  --bind=0.0.0.0:9696 --timeout=100 get_prediction:app