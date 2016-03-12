#!/usr/bin/env python

import ConfigParser
import yaml
import util

from os.path import expanduser, exists
from subprocess import call
from colors import bcolors

def stream_logs(arg_vars, project_root):
  config = ConfigParser.ConfigParser()
  engraver_profile = expanduser("~") + "/.engraver"
  config.read(engraver_profile)
  pem_file_path = config.get('aws', 'pem_file_name', 0)
  remote_user = config.get('aws', 'remote_user', 0)
  container_name = arg_vars['service'] + "_container_name"

  f = project_root + "/ansible/roles/" + arg_vars['service']
  if util.verify_cluster_exists(arg_vars, project_root):
    if exists(f):
      with open(f + "/defaults/main.yml", "r") as stream:
        content = yaml.load(stream)
        if content.get(container_name):
          container = content[container_name]
          call(["ssh", "-t", "-i", pem_file_path, remote_user + "@" + arg_vars['host'], "docker logs -f " + container])
        else:
          print(bcolors.FAIL + "> Service does not define container_name in defaults/main.yml. Cannot stream logs." + bcolors.ENDC)
    else:
      print(bcolors.FAIL + "> Service not found." + bcolors.ENDC)
