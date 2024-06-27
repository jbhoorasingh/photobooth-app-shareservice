
# PhotoBooth-App ShareService
This project is a Python implementation of the PhotoBooth-App ShareService. It provides functionality to upload and save photos to an S3 bucket, replacing the original PHP implementation with a more modern Python-based approach.

## Features
- Upload photos via a web interface
- Save uploaded photos to an S3 bucket
- Lightweight and easy to deploy
- Technologies Used:
  - Python
  - Flask (for the web interface)
  - Boto3 (for interacting with AWS S3)
  - Docker (for containerization, planned)

## Watch: User Exprience
[![Watch the video](http://i3.ytimg.com/vi/agiDfWkOLFE/hqdefault.jpg)](https://youtu.be/agiDfWkOLFE)
## Getting Started: Development
Prerequisites:
- Python 3.10 or higher
- S3 bucket (for storing photos) (tested with AWS S3 and DigitalOcean Spaces) 
- Docker (for future containerization)

### Installation
Clone the repository:
```shell
git clone https://github.com/jbhoorasingh/photobooth-app-shareservice.git
cd photobooth-app-shareservice
Create and activate a virtual environment:
```
```shell
python -m venv .venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install the dependencies:
```

```shell
pip install -r requirements.txt
````

Set environment variables:

Create a .env file in the project root and add the following:
```shell
S3_KEY=your_aws_access_key_id
S3_SECRET=your_aws_secret_access_key
S3_BUCKET=your_s3_bucket_name
S3_ENDPOINT=https://nyc3.digitaloceanspaces.com
S3_REGION=nyc3
S3_SUBFOLDER=photos-e3 # All photos will be saved to this subfolder
PHA_SS_APIKEY=blahblahblahAPIKEYGoeshere
FLASK_HOST=0.0.0.0

```

Running the Application
Start the Flask application:

```shell
python app.py
flask run --reload --debug --host 0.0.0.0 # Alternatively, use the Flask CLI
```


## Photobooth-App ShareService Configuration:
- Navigate to the http://photobooth-hostname:8080/#/admin/ route to access the admin interface.
- Navigate to the Configuration tab and then the share service section.
- Update share service URL to http://ss.photobooth.dev.local:8080/pba-shareservice
- Update the API key to the value set in the .env file (PHA_SS_APIKEY)



## Roadmap
### Todo
#### Update documentation:
Improve and expand the project documentation to provide more details on usage, configuration, and development.

#### Move to an ORM:
Replace direct database interactions with an ORM to simplify data management and improve maintainability.

#### Containerize:
Create Docker configurations to containerize the application for easier deployment and scaling.

#### Add tests:
Write unit and integration tests to ensure the application works as expected and to prevent regressions.

# Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure your code follows the existing style and includes tests where applicable.

# License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
The original PhotoBooth-App team for their inspiration and initial implementation.
The Flask and Boto3 communities for their excellent libraries and documentation.

## Quick Note
If you are thinking about trying this out - please consider using the Digital Ocean referral link below. You will get $200 credit for 60 days, and I will get $25 credit to help run this demo.

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg)](https://www.digitalocean.com/?refcode=0fea2173d2fd&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)
