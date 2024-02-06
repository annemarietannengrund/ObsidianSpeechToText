FROM python:3.11-bullseye

COPY requirements.txt ./

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install git -y
RUN apt-get install -y ffmpeg

RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install "git+https://github.com/openai/whisper.git"
ENV RUNS_ON_DOCKER=1