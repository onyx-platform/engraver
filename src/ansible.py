#!/usr/bin/env python

import ConfigParser

from os.path import expanduser
from os import chdir
from subprocess import call

def invoke_ansible(arg_vars, project_root, playbook):
  config = ConfigParser.ConfigParser()
  engraver_profile = expanduser("~") + "/.engraver"
  config.read(engraver_profile)

  aws_access_key = config.get('aws', 'aws_access_key', 0)
  aws_secret_key = config.get('aws', 'aws_secret_key', 0)
  aws_key_name = config.get('aws', 'aws_key_name', 0)
  pem_file_path = config.get('aws', 'pem_file_name', 0)

  chdir(project_root + "/ansible")

  call(["ansible-playbook", "--private-key", pem_file_path,
        "-i", ",", "-e", "remote_user='ubuntu'",
        "-e", ("onyx_cluster_id=" + arg_vars['cluster_id']),
        "-e", ("aws_key_name=" + aws_key_name),
        "-e", ("aws_access_key=" + aws_access_key),
        "-e", ("aws_secret_key=" + aws_secret_key),
        "-e", ("engraver_root=" + project_root),
        project_root + "/ansible/" + playbook])
