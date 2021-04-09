# Build
FROM python:3.7-slim

## Activate virtualenv
RUN python -m venv /opt/api-env
ENV PATH="/opt/api-env/bin:$PATH"

## Copy code
WORKDIR /api
COPY ./ ./

## Install dependencies
RUN pip install -r requirements.txt

# Serve API
EXPOSE 3000
CMD waitress-serve --port 3000 --call "app.main:serve"
