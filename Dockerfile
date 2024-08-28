FROM python:3.12.3-alpine AS builder

# Tell pipenv to create venv in the current directory
ENV PIPENV_VENV_IN_PROJECT=1

# TODO (riley): set a static version
RUN pip install pipenv

ADD Pipfile.lock Pipfile /usr/src/

WORKDIR /usr/src

RUN /usr/local/bin/pipenv sync

FROM docker.io/python:3.12.3-alpine AS runtime


RUN mkdir -v /usr/src/.venv

COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

WORKDIR /usr/src
COPY . /usr/src


CMD ["/usr/src/.venv/bin/python", "server.py"] 