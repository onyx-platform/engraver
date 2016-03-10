#!/usr/bin/env python

import ConfigParser

from colors import bcolors
from os.path import expanduser
from subprocess import call

def hide_prefix(s):
  return ((len(s[:-4]) * "*") + s[-4:])

def helpful_prompt(p, m, k, hide=False):
  if hide and m.get(k):
    x = raw_input(p + " [" + hide_prefix(m.get(k)) + "]: ")
  elif hide:
    x = raw_input(p + ": ")
  elif m.get(k):
    x = raw_input(p + " [" + m.get(k) + "]: ")
  else:
    x = raw_input(p + ": ")

  if x == "":
    return m.get(k, "")
  else:
    return x

def configure_aws(arg_vars, project_root):
  engraver_profile = expanduser("~") + "/.engraver"
  call(["touch", engraver_profile])

  read_config = ConfigParser.ConfigParser()
  read_config.read(engraver_profile)

  existing = {}
  if 'aws' in read_config.sections():
    existing['aws_access_key'] = read_config.get('aws', 'aws_access_key', 0)
    existing['aws_secret_key'] = read_config.get('aws', 'aws_secret_key', 0)
    existing['aws_key_name'] = read_config.get('aws', 'aws_key_name', 0)
    existing['pem_file_path'] = read_config.get('aws', 'pem_file_name', 0)
    existing['remote_user'] = read_config.get('aws', 'remote_user', 0)

  access_key = helpful_prompt("AWS Access Key ID", existing, 'aws_access_key', hide=True)
  secret_key = helpful_prompt("AWS Secret Access Key", existing, 'aws_secret_key', hide=True)
  aws_key_name = helpful_prompt("AWS SSH key name", existing, 'aws_key_name')
  pem_file_path = helpful_prompt("AWS SSH .pem file location", existing, 'pem_file_path')
  remote_user = helpful_prompt("SSH remote user", existing, 'remote_user')

  config = ConfigParser.ConfigParser()
  config.add_section('aws')
  config.set('aws', 'aws_access_key', access_key)
  config.set('aws', 'aws_secret_key', secret_key)
  config.set('aws', 'aws_key_name', aws_key_name)
  config.set('aws', 'pem_file_name', pem_file_path)
  config.set('aws', 'remote_user', remote_user)

  with open(engraver_profile, "w") as text_file:
    config.write(text_file)

  print(bcolors.OKBLUE + bcolors.BOLD + "> Installed new configuration to " + engraver_profile + bcolors.ENDC)
