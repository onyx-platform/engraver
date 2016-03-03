#!/usr/bin/env python

from colors import bcolors
from subprocess import call
from pkg_resources import resource_filename

def init(arg_vars, project_root):
  app_name = arg_vars['app-name']
  ansible_dir = app_name + "/ansible"

  print(bcolors.OKBLUE + "> Invoking Leiningen and streaming its output ..." + bcolors.HEADER)
  call(["lein", "new", "onyx-app", app_name])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished executing Leiningen." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Initializing .engraver folders ..." + bcolors.ENDC)
  call(["mkdir", "-p", (app_name + "/.engraver")])
  call(["touch", (app_name + "/.engraver/config")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished .engraver folder initialization." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Cloning Ansible playbook from Git. Streaming Git output ..." + bcolors.HEADER)
  call(["git", "clone", "git@github.com:MichaelDrogalis/engraver-ansible.git", ansible_dir])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished cloning playbook." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Initializing Ansible vars directories..." + bcolors.ENDC)
  call(["mkdir", "-p", (ansible_dir + "/group_vars")])
  call(["mkdir", "-p", (ansible_dir + "/cluster_vars")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible vars directory creation." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Creating default Ansible playbook..." + bcolors.ENDC)
  engraver_playbook_file = resource_filename(__name__, "ansible_template/engraver_aws.yml")
  call(["cp", engraver_playbook_file, (ansible_dir + "/engraver_aws.yml")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible default playbook creation." + bcolors.ENDC)
