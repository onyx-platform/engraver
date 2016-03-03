#!/usr/bin/env python

import ConfigParser

from colors import bcolors
from os.path import expanduser
from subprocess import call

def configure_aws(arg_vars, project_root):
  engraver_profile = expanduser("~") + "/.engraver"
  call(["touch", engraver_profile])
  aws_key_name = raw_input("AWS SSH key name: ")
  pem_file_path = raw_input("AWS SSH .pem file location: ")

  config = ConfigParser.ConfigParser()
  config.add_section('aws')
  config.set('aws', 'aws_key_name', aws_key_name)
  config.set('aws', 'pem_file_name', pem_file_path)

  with open(engraver_profile, "w") as text_file:
    config.write(text_file)

  print(bcolors.OKBLUE + bcolors.BOLD + "> Installed new configuration to " + engraver_profile + bcolors.ENDC)
