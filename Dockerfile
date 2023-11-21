FROM python:slim-bookworm

RUN pip install --upgrade pip

COPY requirements.txt /

RUN apt-get -y update
RUN apt-get -y upgrade

RUN pip install --trusted-host pypi.python.org -v -r /requirements.txt

WORKDIR /wifiscan2mqtt

ADD . /wifiscan2mqtt

CMD ["python", "-u", "app.py"]