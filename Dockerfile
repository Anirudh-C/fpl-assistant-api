# Build
FROM python:3.7-slim as build

## Activate virtualenv
RUN python -m venv /opt/api-env
ENV PATH="/opt/api-env/bin:$PATH"

## Copy code
WORKDIR /api
COPY ./ ./

## Install dependencies
RUN pip install -r requirements.txt

# Production
FROM python:3.7-alpine

# Copy code and virtualenv
COPY --from=build /api /api
COPY --from=build /opt/api-env /opt/api-env

# Activate virtualenv
ENV PATH="/opt/api-env/bin:$PATH"

WORKDIR /api

# Serve API
EXPOSE 80
CMD waitress-serve --port 80 --call "app.main:serve"
