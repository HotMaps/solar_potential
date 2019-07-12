FROM hotmaps/base_cm:latest

RES_NINJA_TOKENS="a4a030f47ae97751fb7a36332ec614b3bfc01b8f:672ae47a0f5e8641d58deb8e77d6784e9a3de2f3:113919a0c1ac7d58791d6d86c162b4c121d71bf3:dcfa933f901b54b8f575b5220f0b2eb32229c77e:1fa92f2075efe80ea12e58c475af360d96b3d154:c71765b09c043a05b3ddbe1eb1a9dbc0eb354127:4267381743d9253066ae355fad0a593daddc65ba"


# Setup app server
WORKDIR /
RUN mkdir -p /data

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

