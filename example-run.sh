#!/bin/bash

export CUDA_VISIBLE_DEVICES=0
name="inptb-outptb-untie-in-out"
nohup nice time python main.py --batch_size 20 --data data/penn --dropouti 0.4 --dropouth 0.25 --seed 141 --epoch 500 --embed ../vectors-gigaword.txt --untied --save ${name}.pt 1>${name}.out 2>${name}.err &
nohup nice time python finetune.py --batch_size 20 --data data/penn --dropouti 0.4 --dropouth 0.25 --seed 141 --epoch 500 --untied --save ${name}.pt 1>${name}.finetune.out 2>${name}.finetune.err &
nohup nice time python pointer.py --data data/penn --save ${name}.pt --lambdasm 0.1 --theta 1.0 --window 500 --bptt 5000 1>${name}.pointer.out 2>${name}.pointer.err &
