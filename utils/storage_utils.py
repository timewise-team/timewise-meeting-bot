from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    './timewise-441405-e06d3844723e.json')


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    generation_match_precondition = 0
    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
