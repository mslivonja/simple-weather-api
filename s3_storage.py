import boto3
import io

class S3Service:
    def __init__(self, access_key, secret_key, bucket_name, region_name):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name
        )

    def upload_file(self, file_content:str, file_name:str):
        # Convert string to bytes for upload
        file_obj = io.BytesIO(file_content.encode("utf-8"))
        self.s3_client.upload_fileobj(
            file_obj,
            self.bucket_name,
            file_name,
            ExtraArgs={"ContentType": "text/csv", "ACL": "public-read"}
        )
        return f"http://localhost:9000/{self.bucket_name}/{file_name}"

