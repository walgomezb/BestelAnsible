# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app


# Install any needed packages specified in requirements.txt
RUN pip install flask ansible paramiko ansible-runner  ansible-pylibssh 
RUN ansible-galaxy collection install cisco.ios
RUN apt-get update && apt-get install -y sshpass openssh-client


# Copy the current directory contents into the container at /usr/src/app
COPY get_voice_port_details.yml .
COPY configure_voice_port_paybook.yml .
COPY ./src/playbookRunner.py .


# Expose the port the app runs on
EXPOSE 5499

# Run the Flask app
CMD ["python", "playbookRunner.py"]
