# pull official base image
FROM python:3.11

# Set work directory
RUN mkdir -p /opt/pip_cache
RUN mkdir -p /opt/jamun-assets && chmod -R 777 /opt/

WORKDIR /ATS-resume-code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the port for App Runner
EXPOSE 8000

# Run migrations, collect static files and start the server
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ATSproj.wsgi:application --bind 0.0.0.0:8000"]
