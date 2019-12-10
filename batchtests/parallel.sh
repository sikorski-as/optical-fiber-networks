#!/usr/bin/bash

export PYTHONPATH=.

for i in {1..40}
do
  python3 batchtests/batch_example.py&
done
wait