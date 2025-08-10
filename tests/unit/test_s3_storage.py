from unittest.mock import patch, MagicMock

import pytest
from botocore.config import Config

from s3_storage import S3Service

BUCKET_NAME = "test"

def s3_service():
    return S3Service(
        endpoint="http://localhost:9000",
        bucket_name= BUCKET_NAME,
        access_key= "fake_id",
        secret_key= "fake_secret"
    )

def fake_csv_data() -> str:
    return ("city,location,temp,feels_like,temp_min,temp_max,"
            "pressure,humidity,visibility,wind_speed,description,timestamp\n"
            "Zagreb,Donji grad,35.5,36.94,33.82,35.5,1017,36,10000,2.57,Clear sky,2025-08-10 16:37:01")


@patch("s3_storage.boto3.client")
def test_upload_file_success(mock_boto_client):
    # Mock boto3 client instance
    mock_client_instance = MagicMock()
    mock_boto_client.return_value = mock_client_instance

    # upload_fileobj should just run without exception
    mock_client_instance.upload_fileobj.return_value = None

    file_name = "weather.csv"

    # mock presigned url
    signature = 'F3Cuu0Yj%2FB8bzS5Vu0zqhnecuqI%3D&Expires=1754856460'
    url = f"http://localhost:9000/{BUCKET_NAME}/{file_name}?AWSAccessKeyId=myminioadmin&Signature={signature}"
    mock_client_instance.generate_presigned_url.return_value = url

    # Run method
    file_content = fake_csv_data()

    service = s3_service()
    result_url = service.upload_file(file_content, file_name)

    # Assertions
    mock_boto_client.assert_called_once_with(
        "s3",
        endpoint_url="http://localhost:9000",
        region_name = 'us-east-1',
        aws_access_key_id="fake_id",
        aws_secret_access_key="fake_secret"
    )
    assert result_url == url
    mock_client_instance.upload_fileobj.assert_called_once()


@patch("s3_storage.boto3.client")
def test_upload_file_failure(mock_boto_client):
    # Mock boto3 client instance
    mock_client_instance = MagicMock()
    mock_boto_client.return_value = mock_client_instance

    # Simulate upload error
    mock_client_instance.upload_fileobj.side_effect = Exception("S3 error")

    # Run method
    file_content = fake_csv_data()
    file_name = "weather.csv"
    service = s3_service()

    with pytest.raises(Exception) as excep_info:
        result_url = service.upload_file(file_content, file_name)

        assert "S3 error" in str(excep_info)
        # Assertions
        assert result_url is None
        mock_client_instance.upload_fileobj.assert_called_once()
