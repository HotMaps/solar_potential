#
# hotmaps/cm image Dockerfile
#
#


FROM geographica/gdal2:latest


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
    curl \
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




# Install / update relevant ubuntu packages:
#RUN apt-get update \
 #	&& apt-get install -y --no-install-recommends libgmp3-dev

# Download and install glpk:
 #RUN mkdir /usr/local/glpk \
# 	&& curl http://ftp.gnu.org/gnu/glpk/glpk-4.39.tar.gz \
# 	| tar xvzC /usr/local/glpk --strip-components=1 \
# 	&& cd /usr/local/glpk \
# 	&& ./configure \
# 	&& make \
# 	&& make install





# Setup app server
RUN mkdir -p /data
COPY . /cm
WORKDIR /cm

RUN ls

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    software-properties-common \
    wget

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py


RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn



# Install required python modules


# Copy app source code



EXPOSE 80

# Start server

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CMD ["gunicorn", "--config", "gunicorn-config.py", "--log-config", "app/logging.conf", "run:application"]

# Start processes
CMD ["/usr/bin/supervisord"]


