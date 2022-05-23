FROM python:3.9-slim

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv && \
  pipenv install --system --deploy --clear

COPY . .

EXPOSE 8080

ENTRYPOINT [ "uvicorn", "main:app", "--reload" ]

