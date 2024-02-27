# syntax=docker/dockerfile:1

# Use the official Python image as the base image
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Set the working directory in the container
WORKDIR /hummingbird_server

# Git이 설치되어 있는지 확인하고 설치
RUN apt-get update && apt-get install -y git &&apt-get install wget

# Install any dependencies
RUN git clone -b audio https://github.com/namkidong98/hummingbird_server.git .
RUN cd /hummingbird_server

RUN pip install git+https://github.com/openai/whisper.git
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/yeti-s/chat-hummingbird.git

# Copy the rest of the application code to the working directory
COPY .env .

RUN mkdir FlyAIVoice/model
RUN wget -O FlyAIVoice/model/G_latest.pth https://huggingface.co/Baemsul/hummingbird/resolve/main/G_latest.pth?download=true

# Expose the port that the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
