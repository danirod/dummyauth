# This is the Dockerfile for dummyauth.
#
# This is my first Dockerfile for a Python project.
# Things will get better eventually. Bug reports with
# performance suggestions are welcomed.
#
# This Dockerfile is based on Alpine Linux to favour a lightweight image size.
# Because this is a container, the dependencies declared in the Pipfile are
# installed systemwise. uWSGI is installed to act as an WSGI server.

FROM python:3.6-alpine3.6
LABEL "Author" "Dani Rodríguez <dani@danirod.es>"
WORKDIR /app

# Install dependencies required to build uWSGI (a compiler, kernel headers...)
RUN apk add --no-cache build-base linux-headers

# Install Pipenv and uWSGI
RUN pip install uwsgi --no-cache
RUN pip install pipenv --no-cache

# Pipfile
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN PIP_NO_CACHE_DIR=false pipenv install --deploy --system

# Remaining contents of the application.
COPY . /app

# Run the server using uWSGI.
EXPOSE 5000
ENTRYPOINT ["uwsgi", "-s", ":5000", "--protocol", "http", "--master", "--plugin", "python", "--mount", "/=wsgi:app"]
