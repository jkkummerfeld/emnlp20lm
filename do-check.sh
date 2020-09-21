#!/bin/bash

name="check-original0"
export CUDA_VISIBLE_DEVICES=0
nohup nice time python main.py --data data/penn --save ${name}.pt 1>${name}.out 2>${name}.err &
name="check-original1"
export CUDA_VISIBLE_DEVICES=1
nohup nice time python main.py --data data/penn --save ${name}.pt 1>${name}.out 2>${name}.err &
name="check-original2"
export CUDA_VISIBLE_DEVICES=2
nohup nice time python main.py --data data/penn --save ${name}.pt 1>${name}.out 2>${name}.err &
name="check-original3"
export CUDA_VISIBLE_DEVICES=3
nohup nice time python main.py --data data/penn --save ${name}.pt 1>${name}.out 2>${name}.err &
