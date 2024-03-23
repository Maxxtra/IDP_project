#!/bin/bash

docker stack rm sprc3
docker-compose -f stack.yml down
