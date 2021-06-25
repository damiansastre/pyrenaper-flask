# pyrenaper-flask

Flask implementation for [pyrenaper](https://github.com/tagercito/pyrenaper)

## Documentation

[Postman Documentation](https://documenter.getpostman.com/view/4003274/Tzedg4A8)
## Docker Instalation

Modify docker-compose with api keys

```
web:
  build: .
  ports:
   - "5000:5000"
  volumes:
    - .:/code
  environment:
      FLASK_ENV: development
      PAQUETE1_API_KEY: 'KEY'
      PAQUETE2_API_KEY: 'KEY2'
      PAQUETE3_API_KEY: 'KEY3'

```

The following command will build the docker image

```
docker-compose build
```

Finally run

```
docker-compose up
```

## Endpoints

### Package 1
| URL        | 
| ------------- |
| /scan_barcode      | 
| /new_operation      |
| /add_barcode | 
| /add_front | 
| /add_back |
| /register | 
| end operation|

### Package 2
| URL        | 
| ------------- |
| /face_login      | 


### Package 3
| URL        | 
| ------------- |
| /person_data      | 


## Extra endpoints

| URL        | Description |
| ------------- |:----------:|
| /encode_images      | Encodes: front/back and selfie images into base64 images usable by pyrenaper | 
| /packageone | Runs a full Package 1 flow     |
