from flask import Flask, request, abort, jsonify, send_from_directory, Response, render_template
from werkzeug.utils import secure_filename
import os
import sqlite3
import time
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Configuration options
APIKEY = os.getenv('PHA_SS_APIKEY', 'ranf7912184^!64670bdom68c2939dcfckey3e02a22')
S3_KEY = os.getenv('S3_KEY', 'ranf7912144(64670bdom68c2839dcf)ckey3e02a22')
S3_SECRET = os.getenv('S3_SECRET', 'ranf791414464670b_dom68c2839dcfckey3e02a22')
S3_BUCKET = os.getenv('S3_BUCKET', 'my-space')
S3_ENDPOINT = os.getenv('S3_ENDPOINT', 'https://datacenter.digitaloceanspaces.com')
S3_REGION = os.getenv('S3_REGION', 'datacenter')
S3_SUBFOLDER = os.getenv('S3_SUBFOLDER', 'photos')

# Folder to store the uploaded files temporarily
WORK_DIRECTORY = os.path.join(os.path.dirname(__file__), 'upload')

# Maximum file size allowed for upload
ALLOWED_UPLOAD_MAX_SIZE = 25 * 2 ** 20  # 25MB

# Timeout in seconds for the download to be available, ToDo: recode timeout method
TIMEOUT_DOWNLOAD = 30

# Allowed file types for upload
ALLOWED_UPLOAD_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'image/gif': 'gif',
    'video/mp4': 'mp4',
}

# Database configuration
DB_FILENAME = "jobs.sqlite3"

# Version of the API
VERSION = 2


def initialize_db():
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS upload_requests (
            file_identifier TEXT PRIMARY KEY,
            filename TEXT,
            last_modified TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

# Ensure the database is initialized at startup
with app.app_context():
    initialize_db()

def check_api_key(req_key):
    """
    Check if the API key is valid
    :param req_key:
    :return: abort if the API key is invalid
    """
    if req_key != APIKEY:
        abort(401, description="Invalid API key")


def allowed_file(filename):
    """
    Check if the file type is allowed
    :param filename: Filename to check
    :return: True if the file type is allowed, else False
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_UPLOAD_TYPES.values()


def upload_file_to_s3(file_path, bucket, object_name):
    """
    Upload a file to an S3 bucket

    :param file_path: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_path is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_path
    if object_name is None:
        object_name = file_path
    else:
        object_name = S3_SUBFOLDER + '/' + object_name


    # Upload the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=S3_KEY,
                             aws_secret_access_key=S3_SECRET,
                             region_name=S3_REGION,
                             endpoint_url=S3_ENDPOINT,)
    try:
        response = s3_client.upload_file(file_path, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """
    Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3',
                             aws_access_key_id=S3_KEY,
                             aws_secret_access_key=S3_SECRET,
                             region_name=S3_REGION,
                             endpoint_url=S3_ENDPOINT)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': '{}/{}'.format(S3_SUBFOLDER, object_name)},
                                                    ExpiresIn=expiration)
    except NoCredentialsError:
        print("No AWS credentials found")
        app.logger.error("No AWS credentials found")
        return None

    # The response contains the presigned URL
    return response

@app.route('/')
def hello_world():  # put application's code here
    return render_template('photo_darkroom.html', retry=4, refresh_in=5)
    # return 'Hello World!'


@app.route('/pba-shareservice', methods=['GET', 'POST'])
def pba_shareservice():
    action = request.args.get('action') if request.method == 'GET' else request.form.get('action')
    allowed_actions = ['list', 'download', 'upload', 'info', 'upload_queue']
    if action not in allowed_actions:
        abort(406)

    if action == 'info':
        return jsonify({"version": VERSION, "name": "photobooth-app fileupload extension"})

    elif action == 'upload_queue':

        def generate():
            loop_time = 0.5  # loop every x seconds
            loop_time_max = 240  # after x seconds, the script terminates and the client is expected to create a new connection latest
            time_processed = 0

            try:
                while time_processed <= loop_time_max:
                    conn = sqlite3.connect(DB_FILENAME)
                    c = conn.cursor()
                    c.execute("SELECT * FROM upload_requests WHERE status = 'pending'")
                    results = c.fetchall()
                    conn.close()

                    for result in results:
                        # Get column names from cursor.description
                        column_names = [column[0] for column in c.description]
                        # Create a dictionary from column names and result
                        result_dict = dict(zip(column_names, result))

                        conn = sqlite3.connect(DB_FILENAME)
                        c = conn.cursor()
                        c.execute("UPDATE upload_requests SET status = 'job_assigned' WHERE file_identifier = ?",
                                  (result_dict['file_identifier'],))
                        conn.commit()
                        conn.close()
                        app.logger.debug("Assigned job for file %s", result_dict['file_identifier'])

                        yield '%s\n' % json.dumps(result_dict)

                    if not results:
                        time.sleep(loop_time)
                        time_processed += loop_time
                        # app.logger.debug("No pending uploads, sleeping for %s seconds", loop_time)
                        yield '%s\n' % json.dumps({'ping': time.time()})
            except OSError:
                print("Client disconnected, stopping the response stream.")
                return  # Exit the generator function gracefully

        return Response(generate(), mimetype='text/event-stream')


    elif action == 'download':
        file_id = request.args.get('id')

        if file_id is None:
            abort(400, description="Missing file id")


        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()
        c.execute("SELECT * FROM upload_requests WHERE file_identifier = ? AND status = 'uploaded'", (file_id,))
        # c.execute("SELECT * FROM upload_requests WHERE file_identifier = ? AND (status = 'uploaded' OR status = 'job_assigned')", (file_id,))
        result = c.fetchone()
        print(result)
        app.logger.debug("Result: %s", result)

        # need to also check for job_assigned status

        if result is not None:
            filename = result[1]  # Assuming the filename is the second column in the table
            conn.close()
            app.logger.debug("File %s is ready for download", filename)
            # Generate a presigned URL for the S3 object
            presigned_url = create_presigned_url(S3_BUCKET, filename)
            print(presigned_url)

            return render_template('photo_pickup.html', presigned_url=presigned_url)
        else:
            c.execute(
                "SELECT * FROM upload_requests WHERE file_identifier = ?",
                (file_id,))

            result_ts = c.fetchone()
            print("result_ts")
            print(result_ts)
            app.logger.debug("Result: %s", result_ts)

            if result_ts is None:
                c.execute("INSERT INTO upload_requests (file_identifier, status) VALUES (?, 'pending')", (file_id,))
                conn.commit()
                conn.close()

            if not request.args.get('retry'):
                retry = 1
            else:
                retry = int(request.args.get('retry')) + 1
            if retry > 6:
                return jsonify({"message": "Upload failed, Photobooth might have lost internet"}), 500

            return render_template('photo_darkroom.html', retry=retry, refresh_in=10)


    elif action == 'upload':
        apikey = request.form.get('apikey')
        print("#####################################################")
        print("--- Headers --- \n", request.headers)
        print("--- Form data --- \n", request.form)
        print("--- Query parameters --- \n", request.args)
        print("--- Request files --- \n", request.files)
        print("REQUEST - apiKey")
        print(apikey)
        print("------  -----------  ----- ------  -----------  -----")



        check_api_key(apikey)

        if 'upload_file' not in request.files:
            print(request.files, "No file part in the request")
            abort(400, description="No file part in the request")
        file = request.files['upload_file']
        if file.filename == '':
            print(file.filename, "No selected file")
            abort(400, description="No selected file")
        if file and allowed_file(file.filename):
            if file.content_length > ALLOWED_UPLOAD_MAX_SIZE:
                print(file.content_length, ALLOWED_UPLOAD_MAX_SIZE, "File too large")
                abort(400, description="File too large")
            filename = secure_filename(file.filename)
            file.save(os.path.join(WORK_DIRECTORY, filename))

            upload = upload_file_to_s3(os.path.join(WORK_DIRECTORY, filename), S3_BUCKET, filename)

            file_id = request.form.get('id')
            if not upload:
                conn = sqlite3.connect(DB_FILENAME)
                c = conn.cursor()
                c.execute("REPLACE INTO upload_requests (file_identifier, filename, status) VALUES (?, ?, 'pending')",
                          (file_id, filename))
                conn.commit()
                conn.close()
                print("Upload to S3 failed")
                abort(500, description="Upload to S3 failed")


            # Delete the file from the local storage
            os.remove(os.path.join(WORK_DIRECTORY, filename))

            conn = sqlite3.connect(DB_FILENAME)
            c = conn.cursor()
            c.execute("REPLACE INTO upload_requests (file_identifier, filename, status) VALUES (?, ?, 'uploaded')",
                      (file_id, filename))
            conn.commit()
            conn.close()
            return jsonify({"message": "File successfully uploaded and ready to download"})
        else:
            print(file.content_type, file.filename, file.content_length, ALLOWED_UPLOAD_MAX_SIZE, "File type not allowed")
            abort(400, description="File type not allowed")

if __name__ == '__main__':
    os.makedirs(WORK_DIRECTORY, exist_ok=True)
    initialize_db()

    from dotenv import load_dotenv
    load_dotenv()
    print("is running")
    host = os.getenv('FLASK_HOST', '127.0.0.1')

    app.run(host=host, port=8080, debug=True)
