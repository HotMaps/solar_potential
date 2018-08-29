#
# hotmaps/cm image Dockerfile
#
#


FROM continuumio/miniconda3
RUN conda update -y conda
RUN conda config --add channels conda-forge
RUN conda install -y gdal rasterio geopandas

MAINTAINER lesly Houndole <lesly.houndole@crem.ch>

# setup volume
RUN mkdir -p /data
VOLUME /data

ENV CELERY_BROKER_URL amqp://admin:mypass@rabbit:5672/
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true


# Setup app server
RUN mkdir -p /data
COPY . /cm
WORKDIR /cm

RUN ls


RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py


RUN pip install -r requirements.txt
RUN pip install gunicorn



# Install required python modules


# Copy app source code



EXPOSE 5001

# Start server

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CMD ["gunicorn", "--config", "gunicorn-config.py", "--log-config", "app/logging.conf", "run:application"]

# Start processes
CMD ["/usr/bin/supervisord"]


