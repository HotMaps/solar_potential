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
    supervisor \
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






WORKDIR /
RUN mkdir -p /data

# Install pip
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py



RUN cd /opt && git clone https://github.com/hotmaps/reslib.git --branch develop\
    && cd reslib && pip3 install .
RUN cd /opt && git clone https://github.com/hotmaps/resutils.git \
    && cd resutils && pip3 install .


RUN pip3 install gunicorn




# Install required python modules
COPY ./requirements.txt /cm/
RUN pip3 install -r /cm/requirements.txt

# Copy app source code
COPY . /cm
WORKDIR /cm

RUN chmod u+x /cm/wait-for-it.sh

# Start server
EXPOSE 80

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start processes
CMD ["/cm/wait-for-it.sh","rabbit:5672","--strict","--timeout=360","--","/usr/bin/supervisord"]

