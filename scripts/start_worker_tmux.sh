#!/bin/bash
SESSION="worker_example"
CMD="cd $(pwd)/scripts && python worker_example.py"

tmux new-session -d -s $SESSION "$CMD"
