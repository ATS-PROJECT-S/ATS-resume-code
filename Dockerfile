# pull official base image
FROM python:3.11

# set work directory

RUN mkdir -p /opt/pip_cache
RUN mkdir -p /opt/jamun-assets && chmod -R 777 /opt/

WORKDIR /ATS-resume-code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

#EXPOSE 8000

CMD ["python manage.py migrate"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
