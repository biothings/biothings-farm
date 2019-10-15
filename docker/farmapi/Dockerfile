FROM ubuntu:18.04
LABEL maintainer "help@biothings.io"

ARG PROD
ARG BIOTHINGS_GIT_VERSION
ARG FARM_GIT_VERSION
RUN if [ -z "$BIOTHINGS_GIT_VERSION" ]; then echo "NOT SET - use --build-arg BIOTHINGS_GIT_VERSION=..."; exit 1; else : ; fi
RUN if [ -z "$FARM_GIT_VERSION" ]; then echo "NOT SET - use --build-arg FARM_GIT_VERSION=..."; exit 1; else : ; fi

RUN apt-get -y update
RUN apt-get install -y apt-utils python-yaml python-jinja2 git python3 apt-transport-https curl bash vim tmux sudo htop ne wget net-tools nginx
RUN git clone http://github.com/ansible/ansible.git /tmp/ansible
WORKDIR /tmp/ansible
ENV PATH /tmp/ansible/bin:/sbin:/usr/sbin:/usr/bin:/bin:/usr/local/bin
ENV ANSIBLE_LIBRARY /tmp/ansible/library
ENV PYTHONPATH /tmp/ansible/lib:$PYTHON_PATH

ADD ansible_playbook /tmp/ansible_playbook
ADD inventory /etc/ansible/hosts

WORKDIR /tmp/ansible_playbook
RUN ansible-playbook farm_hub.yml \
                     -e "biothings_git_version=$BIOTHINGS_GIT_VERSION" \
                     -e "farm_git_version=$FARM_GIT_VERSION" \
                     -e "prod=$PROD" \
                     -c local

# Clean up ansible_playbook
WORKDIR /tmp
RUN if [ -n "$PROD" ]; then rm -rf /tmp/ansible_playbook; fi
RUN if [ -n "$PROD" ]; then rm -rf /tmp/ansible; fi


EXPOSE 7022 7080
VOLUME ["/data"]
ENTRYPOINT ["/docker-entrypoint.sh"]
