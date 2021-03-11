FROM python:3.8-slim-buster as python-base

WORKDIR /
COPY ./ /snowshupostgres_docker_build

RUN apt-get update && \
    apt-get install vim -y && \
    python3 -m pip install --upgrade pip && \
    pip3 install -r /snowshupostgres_docker_build/dev_requirements.txt && \
    pip3 install /snowshupostgres_docker_build/snowshupostgres/

ENTRYPOINT [ "/snowshupostgres_docker_build/entry_point.sh" ]
CMD [ "bash" ]