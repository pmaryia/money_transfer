FROM python:3.12

RUN pip install poetry

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./pyproject.toml ./poetry.lock ./scripts/entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

RUN poetry install --without dev --no-root

COPY . .

EXPOSE 8000

CMD ./entrypoint.sh
