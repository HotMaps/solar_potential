#
# hotmaps/cm image Dockerfile
#
#

FROM ubuntu:16.04


ENV CELERY_BROKER_URL amqp://admin:mypass@rabbit:5672/
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true


MAINTAINER lesly Houndole <lesly.houndole@crem.ch>

# setup volume
RUN mkdir -p /data
VOLUME /data


# Build commands
RUN apt-get update && apt-get dist-upgrade -y && apt-get autoremove -y

# Install required software

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    software-properties-common \
    wget \
    gdal-bin \
    ca-certificates \
    gcc \
    git \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    python-gdal \
    make \
    python-pip \
    python2.7 \
    python2.7-dev \
    ssh \
    && apt-get autoremove \
    && apt-get clean


RUN pip install -U "setuptools==38.5.1"

RUN pip install -U "pip==10.0.1"
RUN pip install setuptools --upgrade




# Setup app server
RUN mkdir -p /data
COPY . /cm
WORKDIR /cm

RUN ls

# Install required python modules

RUN pip install -r requirements.txt

# Copy app source code



EXPOSE 5001

# Start server
#CMD ["gunicorn", "--config", "gunicorn-config.py", "--log-level", "debug", "run:application"]
#CMD gunicorn -b 0.0.0.0:5001 --access-logfile - "run:application"
CMD ./run_cm_services.sh



