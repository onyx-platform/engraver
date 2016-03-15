#!/usr/bin/env python

import yaml
import util

from prettytable import PrettyTable
from subprocess import call
from colors import bcolors, print_ok, print_ok_pending, print_done
from os import listdir, walk, chdir
from os.path import exists

def service_new(arg_vars, project_root):
  print_ok_pending("Invoking ansible-galaxy. Streaming its output")
  role = util.service_path(project_root, arg_vars['service-name'])
  call(["ansible-galaxy", "init", role])
  print_done("Service role created. Edit at: " + role)

def service_remove(arg_vars, project_root):
  role = util.service_path(project_root, arg_vars['service-name'])
  call(['rm', '-rf', role])
  print_ok("Deleted service: " + arg_vars['service-name'])

def service_pull(arg_vars, project_root):
  print_ok_pending("Invoking Git. Streaming its output")
  role = util.service_path(project_root, arg_vars['service-name'])
  call(["git", "clone", arg_vars['service-repo'], role])
  call(["rm", "-rf", role + "/.git"])
  print_ok("Installed service to " + role)

def service_describe(arg_vars, project_root):
  path = project_root + "/ansible/roles"
  services = next(walk(path))[1]
  t = PrettyTable(['Service Name', 'Dependencies'])
  t.align = "l"

  for s in services:
    f = project_root + "/ansible/roles/" + s + "/defaults/main.yml"
    if exists(f):
      with open(f, "r") as stream:
        content = yaml.load(stream) or {}
        t.add_row([s, ", ".join(content.get('service_dependencies', []))])
    else:
      t.add(row([s, '']))

  print t
