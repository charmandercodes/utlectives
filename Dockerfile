
FROM node:18 AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build



# Image: Python 3.11
FROM python:3.11

# prevents django from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# ensures that the output from python is sent straight to terminal (e.g. for logging)
ENV PYTHONUNBUFFERED=1

# set the working directory in the container
WORKDIR /app

# commands 

COPY requirements.txt /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# copy the current directory contents into the container at /app
COPY . /app

# Copy built assets from frontend stage
COPY --from=frontend /app/assets ./static/assets
# Run collectstatic during image build
RUN python manage.py collectstatic --noinput

# collecstatic

RUN python manage.py collectstatic --noinput

# make port 8000 available to the world outside this container

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]








