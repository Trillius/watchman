#!/bin/bash
SESSION="watchman_server"
CMD="cd $(pwd)/bot && python main.py"

tmux new-session -d -s $SESSION "$CMD"
