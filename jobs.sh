#!/bin/bash
cd /home/brian_oyollo/Documents/projects/demuro/Cars-and-Bids/
source env/bin/activate

python /home/brian_oyollo/Documents/projects/demuro/Cars-and-Bids/listing.py
python /home/brian_oyollo/Documents/projects/demuro/Cars-and-Bids/etl.py
python /home/brian_oyollo/Documents/projects/demuro/Cars-and-Bids/upload.py