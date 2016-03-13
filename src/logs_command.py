#!/usr/bin/env python

import ConfigParser
import yaml
import util

from os.path import expanduser, exists
from subprocess import call
from colors import bcolors, print_ok, print_fail

def stream_logs(arg_vars, project_root):
  config = ConfigParser.ConfigParser()
  engraver_profile = expanduser("~") + "/.engraver"
  config.read(engraver_profile)
  pem_file_path = config.get('aws', 'pem_file_name', 0)
  remote_user = config.get('aws', 'remote_user', 0)
  service = arg_vars['service']
  container_name = service + "_container_name"

  f = util.service_path(project_root, service)
  if util.verify_cluster_exists(arg_vars, project_root):
    if exists(f):
      with open(f + "/defaults/main.yml", "r") as stream:
        content = yaml.load(stream)
        if content.get(container_name):
          container = content[container_name]
          call(["ssh", "-t", "-i", pem_file_path, remote_user + "@" + arg_vars['host'], "docker logs -f " + container])
        else:
          base = "Service does not define {0}_container_name in defaults/main.yml of its Ansible role. Cannot stream logs."
          print_fail(base.format(service))
    else:
      print_fail("Service not found.")
