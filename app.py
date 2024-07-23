from flask import Flask, jsonify, render_template_string
from flasgger import Swagger
import boto3
import yaml
import os
from botocore.credentials import Credentials
from flask_swagger_ui import get_swaggerui_blueprint

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variable
access_key = os.getenv('access_key')
secret_key = os.getenv('secret_key')

app = Flask(__name__)

# Function to fetch YAML file from S3
credentials = Credentials(
    access_key=access_key,
    secret_key=secret_key,
)

s3 = boto3.client('s3', aws_access_key_id=credentials.access_key,
                  aws_secret_access_key=credentials.secret_key,
                  aws_session_token=credentials.token)


def fetch_yaml_from_s3(bucket_name, file_key):
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    yaml_content = obj['Body'].read().decode('utf-8')
    return yaml_content

# Endpoint to fetch and display Swagger UI


@app.route('/swagger.json')
def swagger_json():
    # Replace 'your-bucket-name' and 'swagger.yaml' with your S3 bucket name and file name
    yaml_content = fetch_yaml_from_s3('viveros-anaya', 'swagger.yaml')
    yaml_content_yaml = yaml.safe_load(yaml_content)

    return jsonify(yaml_content_yaml)


SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/swagger.json'  # Our API url (can be a local or remote URL)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Your Application Name"
    },
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
