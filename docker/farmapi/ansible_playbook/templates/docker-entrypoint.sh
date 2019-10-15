#!/bin/bash

set -u

# check env properly set (they come from "docker run -e ...")
if [ -z "$ES_HOST" ]; then echo ES_HOST not set; exit 1; else : ; fi

# propagate env
echo "# farm hub env" >> ~biothings/.bashrc
echo "export ES_HOST=$ES_HOST" >> ~biothings/.bashrc

service ssh start
service nginx start

# Launch hub in a tmux session
su - biothings -c "
source ~/pyenv/bin/activate
cd
cd standalone && git reset --hard && git pull && pip install -r requirements.txt && cd ..
cd biothings-farm && git reset --hard && git pull && cd ..
# last one to override requirement_web.txt from app
cd biothings.api && git reset --hard && git pull && pip install -r requirements.txt && cd ..
"


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
  if [[ $@ ]]; then 
    eval $@
  fi
  ps auxgww
  SUPERVISOR_PARAMS='-c /etc/supervisor/supervisord.conf'
  supervisord -n $SUPERVISOR_PARAMS
fi
