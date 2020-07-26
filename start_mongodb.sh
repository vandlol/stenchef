#!/bin/bash
mkdir -p data/db/
sudo mongod --dbpath data/db/ 2>&1 >/dev/null &
