#!/bin/bash

cat dofred.txt | xargs -I CMD --max-procs=16 bash -c CMD
