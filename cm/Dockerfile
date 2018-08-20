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
    ssh \
    && apt-get autoremove \
    && apt-get clean









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

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CMD ["gunicorn", "--config", "gunicorn-config.py", "--log-config", "app/logging.conf", "run:application"]

# Start processes
CMD ["/usr/bin/supervisord"]


