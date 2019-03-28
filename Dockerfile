FROM python:3.7-alpine

# create a new non-root user and install apk dependencies
RUN addgroup -S tornado && \
    adduser -S tornado -G tornado

# change the working directory to the new user
WORKDIR /home/tornado

# copy the pip related files
COPY ./Pipfile .
COPY ./Pipfile.lock .

# install pipenv and python dependencies
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

# expose the tornado server port
EXPOSE 8888

# default environment variables
ENV PROD true

# change to the non-root user and start the tornado server
USER tornado

# copy only the necesary code files
COPY ./server.py .
COPY ./settings.py .
COPY --chown=tornado ./aswwu ./aswwu

# start the server
ENTRYPOINT ["python3", "server.py"]
