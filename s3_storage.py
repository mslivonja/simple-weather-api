import boto3
import io
from urllib.parse import urlparse, urlunparse

class S3Service:
    def __init__(self, endpoint, access_key, secret_key, bucket_name, region_name = 'us-east-1'):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = boto3.client(
            "s3",
            endpoint_url = endpoint,
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
            region_name = region_name
        )

    def upload_file(self, file_content:str, file_name:str):
        # Convert string to bytes for upload
        file_obj = io.BytesIO(file_content.encode("utf-8"))

        # Upload object
        self.s3_client.upload_fileobj(
            file_obj,
            self.bucket_name,
            file_name,
            ExtraArgs={"ContentType": "text/csv", "ACL": "public-read"}
        )

        # Generate URL valid for 1 hour
        url = self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket_name, "Key": file_name},
            ExpiresIn=3600  # seconds
        )

        parsed = urlparse(url)
        new_netloc = parsed.netloc.replace("minio", "localhost")
        return urlunparse(parsed._replace(netloc=new_netloc))

