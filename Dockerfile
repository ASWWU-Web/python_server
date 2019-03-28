FROM python:3.7-alpine

# create a new non-root user and install apk dependencies
RUN adduser -S tornado

# change the working directory to the new user
WORKDIR /home/tornado

# only copy the files needed to run the server
COPY ./Pipfile .
COPY ./Pipfile.lock .
COPY ./server.py .
COPY ./settings.py .
COPY ./aswwu ./aswwu

# install pipenv and python dependencies
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

# expose the tornado server port
EXPOSE 8888

# default environment variables
ENV PROD true

# change to the non-root user and start the tornado server
USER tornado
ENTRYPOINT ["python3", "server.py"]
