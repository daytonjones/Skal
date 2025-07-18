# skal/Dockerfile
FROM python:3.12-slim

# set workdir
WORKDIR /app

# system deps for Pillow and Postgres client tools
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# copy application source and entrypoint
COPY . .
RUN chmod +x /app/entrypoint.sh

# collect static files
RUN python manage.py collectstatic --noinput

# expose Django port
EXPOSE 8000

# start Gunicorn
CMD ["gunicorn", "skal.wsgi:application", "--bind", "0.0.0.0:8000"]

