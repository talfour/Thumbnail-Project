## Installation

Make sure you have docker and docker-compose installed.
Clone repository:
```bash
git clone https://github.com/talfour/Thumbnail-Project.git
```

Change current dir
```bash
cd Thumbnail-Project
```

and run following commands:

```bash
docker-compose build
```

## To run the tests

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
