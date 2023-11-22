FROM python:3.7-alpine
COPY requirements.txt /app/
COPY main.py /app/
RUN pip install -r /app/requirements.txt
RUN mkdir data
ENTRYPOINT python /app/main.py
