# Use an official Python runtime as a parent image
FROM python:3.10-slim-bookworm as base

LABEL authors="Jermaine Bhoorasingh"

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    nginx
#    gosu

# Create a group and user
#RUN addgroup --system pbass_app_user && adduser --system --home /app --shell /bin/bash --group pbass_app_user

# Copy requirements.txt and install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/sites-available/default

# Change the ownership of the application directory
#RUN chown -R pbass_app_user:pbass_app_user /app


# Change ownership of /tmp directory
#RUN chown -R pbass_app_user:pbass_app_user /tmp

# Use gosu to step down from root to pbass_app_user
#CMD service nginx start && gosu pbass_app_user uwsgi --ini app.ini

#CMD service nginx start && uwsgi --ini app.ini
CMD uwsgi --ini app.ini