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

RUN chmod u+x /cm/wait-for-it.sh

# Start server
EXPOSE 80

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start processes
CMD ["/cm/wait-for-it.sh","rabbit:5672","--strict","--timeout=360","--","/usr/bin/supervisord"]

