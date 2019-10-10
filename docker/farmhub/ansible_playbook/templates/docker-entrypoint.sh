#!/bin/bash

#set -e
set -u


# Launch hub in a tmux session
su - biothings -c "
source ~/pyenv/bin/activate
cd
cd standalone && git reset --hard && git pull && pip install -r requirements.txt && cd ..
cd
# last one to override requirement_web.txt from app
cd biothings.api && git reset --hard && git pull && pip install -r requirements.txt && cd ..
tmux new-session -d -s hub
tmux send-keys 'cd standalone;  python bin/autohub.py ~/biothings-farm/src' C-m
tmux detach -s hub"

if [ "$?" != "0" ]
then
    echo "Unable to start hub"
    exit 255
fi

# We have TTY, so probably an interactive container...
if test -t 0; then
  # Some command(s) has been passed to container? Execute them and exit.
  # No commands provided? Run bash.
  if [[ $@ ]]; then 
    eval $@
  else 
    export PS1='[\u@\h : \w]\$ '
    /bin/bash
  fi

# Detached mode? Run supervisord in foreground, which will stay until container is stopped.
else
  # If some extra params were passed, execute them before.
  # @TODO It is a bit confusing that the passed command runs *before* supervisord, 
  #       while in interactive mode they run *after* supervisor.
  #       Not sure about that, but maybe when any command is passed to container,
  #       it should be executed *always* after supervisord? And when the command ends,
  #       container exits as well.
  echo "not interactive"
  if [[ $@ ]]; then 
    eval $@
  fi
  echo "onela"
  ps auxgww
  tail -f /dev/null
fi

