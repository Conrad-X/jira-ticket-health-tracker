# Use the official Python image
FROM python:3.9-slim

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Set environment variables
ENV SES_REGION=us-east-1 \
    SES_SENDER= \
    SES_RECIPIENT= \
    AWS_ACCESS_KEY_ID= \
    AWS_SECRET_ACCESS_KEY=

# Command to run the Python script
CMD ["python", "trigger_scripts_and_email.py"]
