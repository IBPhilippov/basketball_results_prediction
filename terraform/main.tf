terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
}

resource "google_project_service" "enabled_apis" {
  project  = var.project
  for_each = toset(var.gcp_service_list)
  service  = each.key
  disable_on_destroy = false
}

resource "time_sleep" "wait_project_init" {
  create_duration = "120s"

  depends_on = [google_project_service.enabled_apis]
}

resource "google_storage_bucket" "data-lake-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true
  depends_on = [time_sleep.wait_project_init]


  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "random_id" "bucket_prefix" {
  byte_length = 16
}

resource "google_pubsub_topic" "input" {
  name = "predictions-input"
  depends_on = [time_sleep.wait_project_init]

}

resource "google_pubsub_topic" "output" {
  name = "predictions-output"
  depends_on = [time_sleep.wait_project_init]

}

resource "google_storage_bucket" "function_bucket" {
  name                        = "${random_id.bucket_prefix.hex}-${var.project}-mlflow" # Every bucket name must be globally unique
  location                    = var.location
  uniform_bucket_level_access = true
  depends_on = [time_sleep.wait_project_init]

}

data "archive_file" "default" {
  type        = "zip"
  output_path = "/tmp/function-source.zip"
  source_dir  = "/app/function_source/"
  depends_on = [time_sleep.wait_project_init]

}

resource "google_storage_bucket_object" "function_bucket" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = data.archive_file.default.output_path # Path to the zipped function source code
  depends_on = [time_sleep.wait_project_init]

}

resource "google_cloudfunctions2_function" "default" {
  name        = "make_prediction"
  location    = "us-central1"
  description = "function that predicts result of the match"
  depends_on = [time_sleep.wait_project_init]

  build_config {
    runtime     = "python39"
    entry_point = "predictFromPubSub" # Set the entry point

    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.function_bucket.name
      }
    }
  }

  service_config {
    max_instance_count = 3
    min_instance_count = 1
    available_memory   = "512M"
    timeout_seconds    = 60
    environment_variables = {
      SERVICE_CONFIG_TEST = "config_test"
    }
    ingress_settings               = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true
    #service_account_email          = google_service_account.default.email
    #service_account_email = provider.google.email
  }

  event_trigger {
    trigger_region = "us-central1"
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.input.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}

resource "google_pubsub_subscription" "read" {
  name  = "read"
  topic = google_pubsub_topic.output.id
  depends_on = [time_sleep.wait_project_init]

  labels = {
    foo = "bar"
  }
  message_retention_duration = "1200s"
  retain_acked_messages      = true
  ack_deadline_seconds = 20

  expiration_policy {
    ttl = "300000.5s"
  }
  retry_policy {
    minimum_backoff = "10s"
  }
  enable_message_ordering    = false
}