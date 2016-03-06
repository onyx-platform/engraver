#!/usr/bin/env python

import ConfigParser

from os.path import expanduser
from subprocess import call

def stream_logs(arg_vars, project_root):
  config = ConfigParser.ConfigParser()
  engraver_profile = expanduser("~") + "/.engraver"
  config.read(engraver_profile)
  pem_file_path = config.get('aws', 'pem_file_name', 0)

  call(["ssh", "-t", "-i", pem_file_path, "ubuntu@" + arg_vars['host'], "docker logs -f " + arg_vars['service']])
