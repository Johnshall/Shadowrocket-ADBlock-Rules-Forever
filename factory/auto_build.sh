#!/bin/bash

Path=./factory
cd $Path

python3 ad.py
python3 gfwlist.py
python3 build_confs.py
python3 build_confs_loon.py
