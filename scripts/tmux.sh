#!/usr/bin/env bash

SESS_NAME="bible"
EDITOR="vim"

tmux new -d -s "$SESS_NAME"
tmux rename-window -t "$SESS_NAME" run

tmux new-window -t "$SESS_NAME"
tmux rename-window -t "$SESS_NAME" code

tmux split-window -t "$SESS_NAME:code" -h

tmux send-keys -t "$SESS_NAME:code.1" "ipython scripts/test.py -i" "C-m"
tmux send-keys -t "$SESS_NAME:code.0" "cd bible_extractor && $EDITOR *.py" "C-m"

tmux attach
