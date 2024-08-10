variable "credentials" {
  description = "Credentials"

}


variable "project" {
  description = "Project"
}

variable "location" {
  description = "Project Location"
}


variable "gcs_bucket_name" {
  description = "Storage Bucket Name"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}

variable "gcp_service_list" {
  type        = list(string)
  description = "The list of apis necessary for the project"
  default     = ["serviceusage.googleapis.com","cloudresourcemanager.googleapis.com","cloudfunctions.googleapis.com","pubsub.googleapis.com",
  "eventarc.googleapis.com","logging.googleapis.com","run.googleapis.com","artifactregistry.googleapis.com",
  "cloudbuild.googleapis.com","bigquery.googleapis.com","bigquerystorage.googleapis.com",
  "iam.googleapis.com", "compute.googleapis.com","serviceusage.googleapis.com"]
}