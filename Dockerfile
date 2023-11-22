FROM python:slim-bookworm

RUN pip install --upgrade pip

RUN apt-get -y update
RUN apt-get -y upgrade

COPY requirements.txt /
RUN pip install --trusted-host pypi.python.org -v -r /requirements.txt
RUN apt-get -y install network-manager

WORKDIR /wifiscan2mqtt

ADD . /wifiscan2mqtt

CMD ["python", "-u", "app.py"]
