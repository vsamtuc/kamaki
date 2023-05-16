FROM debian

# Install Python Setuptools
RUN apt-get update && apt-get install -y python2 wget ca-certificates --no-install-recommends

# Bundle app source
ADD . /src

# Install test requirements
RUN wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
RUN python2 get-pip.py
RUN python2 -m pip install mock ansicolors

# Initialize app environment
WORKDIR /src
RUN python2 setup.py install
