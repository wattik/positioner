FROM python:3.9-slim-buster

RUN apt update
RUN apt-get update && apt-get -y install gcc musl-dev

RUN apt-get -y install python3-swiglpk
RUN apt-get -y install glpk-utils

ENV CVXOPT_BUILD_GLPK=1
ENV CVXOPT_GLPK_LIB_DIR=/usr/lib
ENV CVXOPT_GLPK_INC_DIR=/usr/include
RUN pip install cvxopt

WORKDIR /job

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "sweeper.py"]
