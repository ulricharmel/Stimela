FROM stimela/base:1.4.6
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python3-casacore \
    casacore-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install git+https://github.com/ratt-ru/shadeMS.git@b040
#RUN pip install git+https://github.com/o-smirnov/datashader
RUN pip install -I numpy scabha
RUN shadems -h
