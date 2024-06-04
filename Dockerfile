FROM python:3.12.3-alpine AS builder

# Tell pipenv to create venv in the current directory
ENV PIPENV_VENV_IN_PROJECT=1

# TODO (riley): set a static version
RUN pip install pipenv

# Pipfile contains requests
ADD Pipfile.lock Pipfile /usr/src/

WORKDIR /usr/src

RUN /usr/local/bin/pipenv sync

RUN /usr/src/.venv/bin/python -c "import requests; print(requests.__version__)"

FROM docker.io/python:3.12.3-alpine AS runtime


RUN mkdir -v /usr/src/.venv

COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

RUN /usr/src/.venv/bin/python -c "import requests; print(requests.__version__)"

WORKDIR /usr/src
COPY . /usr/src


# Creates a non-root user and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /usr/src
USER appuser

CMD ["/usr/src/.venv/bin/python", "server.py"] 