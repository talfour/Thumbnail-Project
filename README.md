## Installation

Make sure you have docker and docker-compose installed.
Clone repository and run following commands:

```bash
docker-compose up --build
```

## To make sure everything works correctly

To test run following command:

```bash
docker-compose run --rm backend sh -c "python manage.py test"
```

## Create a super user

```bash
docker-compose run --rm backend sh -c "python manage.py createsuperuser"
```

## Run the server

```bash
docker-compose up
```
