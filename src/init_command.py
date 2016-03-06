#!/usr/bin/env python

import json

from colors import bcolors
from subprocess import call
from pkg_resources import resource_filename

def init(arg_vars, project_root):
  app_name = arg_vars['app-name']
  ansible_dir = app_name + "/ansible"
  roles_dir = ansible_dir + "/roles"

  print(bcolors.OKBLUE + "> Invoking Leiningen and streaming its output ..." + bcolors.HEADER)
  call(["lein", "new", "onyx-app", app_name, "+docker"])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished executing Leiningen." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Initializing .engraver folders ..." + bcolors.ENDC)
  call(["mkdir", "-p", (app_name + "/.engraver")])
  with open((app_name + "/.engraver/config.json"), "w") as text_file:
    json.dump({'organization': arg_vars['organization']}, text_file)
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished .engraver folder initialization." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Creating new Ansible playbook. Streaming Ansible output ..." + bcolors.HEADER)
  call(["ansible-galaxy", "init", ansible_dir])
  call(["cp", resource_filename(__name__, "ansible_template/ansible.cfg"), ansible_dir])
  call(["cp", resource_filename(__name__, "ansible_template/refresh_cache.yml"), ansible_dir])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished executing Ansible." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Cloning Ansible AWS playbook from Git. Streaming Git output ..." + bcolors.HEADER)
  call(["git", "clone", "https://github.com/onyx-platform/engraver-aws.git", roles_dir + "/aws"])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished cloning playbook." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Cloning Ansible Docker playbook from Git. Streaming Git output ..." + bcolors.HEADER)
  call(["git", "clone", "https://github.com/onyx-platform/engraver-docker.git", roles_dir + "/docker"])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished cloning playbook." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Cloning Ansible ZooKeeper playbook from Git. Streaming Git output ..." + bcolors.HEADER)
  call(["git", "clone", "https://github.com/onyx-platform/engraver-zookeeper.git", roles_dir + "/zookeeper"])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished cloning playbook." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Cloning Ansible Onyx playbook from Git. Streaming Git output ..." + bcolors.HEADER)
  call(["git", "clone", "https://github.com/onyx-platform/engraver-onyx.git", roles_dir + "/onyx"])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished cloning playbook." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Initializing Ansible vars directories..." + bcolors.ENDC)
  call(["mkdir", "-p", (ansible_dir + "/group_vars")])
  call(["mkdir", "-p", (ansible_dir + "/vars/cluster_vars")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible vars directory creation." + bcolors.ENDC)
  print("")
