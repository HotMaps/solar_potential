FROM hotmaps/base_cm:latest


# Setup app server
WORKDIR /
RUN mkdir -p /data

# Install required python modules
COPY ./requirements.txt /cm/
RUN pip3 install -r /cm/requirements.txt

# Copy app source code
COPY . /cm
WORKDIR /cm


# Start server
EXPOSE 80

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start processes
CMD ["/usr/bin/supervisord"]


