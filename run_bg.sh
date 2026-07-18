#!/bin/bash
cd /root/JEDI || exit 1
exec nohup python3 -u train_fast.py </dev/null >train_fast.out 2>&1
