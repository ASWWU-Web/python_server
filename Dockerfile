FROM python:3.7-alpine

# create a new non-root user and install apk dependencies
RUN adduser -S tornado

# change the working directory to the new user
WORKDIR /home/tornado

# only copy the files needed to run the server
COPY ./requirements.txt .
COPY ./server.py .
COPY ./settings.py .
COPY ./aswwu .

# install the python dependencies and delete the alpine build dependencies
RUN pip install --no-cache-dir -r requirements.txt

# expose the tornado server port
EXPOSE 8888

# change to the non-root user and start the tornado server
USER tornado
ENTRYPOINT ["python3", "server.py"]
