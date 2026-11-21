FROM python:3.11
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

# Copying source in current directory into the image
# python:3-onbuild expects the source in /usr/src/app
COPY . /usr/src/app




# Commands in a list
CMD ["python", "api.py"]
