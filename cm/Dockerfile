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


ENV RES_NINJA_TOKENS="a4a030f47ae97751fb7a36332ec614b3bfc01b8f:672ae47a0f5e8641d58deb8e77d6784e9a3de2f3:113919a0c1ac7d58791d6d86c162b4c121d71bf3:dcfa933f901b54b8f575b5220f0b2eb32229c77e:1fa92f2075efe80ea12e58c475af360d96b3d154:c71765b09c043a05b3ddbe1eb1a9dbc0eb354127:4267381743d9253066ae355fad0a593daddc65ba"

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
RUN pip3 install https://github.com/hotmaps/reslib.git
RUN pip3 install git+https://github.com/hotmaps/resutils.git
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


