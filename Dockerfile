FROM apache/airflow:latest

USER root

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B7B3B788A8D3785C
RUN apt update
RUN apt install default-jdk -y

ENV JAVA_HOME /usr/lib/jvm/default-java/
RUN export JAVA_HOME

USER airflow

# WORKDIR /app

# COPY requirements.txt /app

# RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install pyspark