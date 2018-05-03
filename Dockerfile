FROM python:3.6-alpine3.6

LABEL "Author" "Dani Rodríguez <dani@danirod.es>"

WORKDIR /app

# Install Pipenv
RUN pip install pipenv

# Copy Pipfile
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# Install dependencies to system pip (to avoid using pipenv)
RUN pipenv install --deploy --system

# Copy remaining contents of the application.
COPY . /app

EXPOSE 5000

ENV FLASK_ENV="production"
ENV FLASK_DEBUG=0

# TODO: You are running directly the Flask development server. This should
# replaced with Gunicorn or another better alternative than pure Flask.
ENTRYPOINT ["python", "wsgi.py"]
