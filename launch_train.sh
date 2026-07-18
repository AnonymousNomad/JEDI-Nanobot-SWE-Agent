#!/bin/bash
cd /root/JEDI || exit 1
rm -f train_fast.log train_fast.out
nohup python3 train_fast.py > train_fast.out 2>&1 &
PID=$!
echo $PID > /root/JEDI/train_fast.pid
echo "Launched training with PID: $PID"
