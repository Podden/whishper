FROM python:3.9-slim

WORKDIR /app

COPY ./app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

EXPOSE 8080

# Set the FLASK_APP environment variable
ENV FLASK_APP=main.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]