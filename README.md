# Parking Lot

This is a representation of a parking lot.

## Dependencies

- Docker >= 20.10.9
- Docker Compose >= 1.27.4

## How to run

```bash
make run
```

1. Go to [http://localhost:9000/docs](http://localhost:9000/docs)

## How to run tests

```bash
make run
```

Open new terminal and run:

```bash
docker ps

docker exec -it <CONTAINER_ID> /bin/bash

python -m pytest
```

## Config file

To change Parking Lot tariffs, free time, please use the following config file:

```bash
app/
    ...
    config.json
    ...
...
```
