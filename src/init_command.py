#!/usr/bin/env python

import json

from colors import bcolors, print_ok, print_ok_pending, print_done
from subprocess import call
from pkg_resources import resource_filename

def drop_git(path):
  call(["rm", "-rf", path + "/.git"])

def init(arg_vars, project_root):
  app_name = arg_vars['app-name']
  ansible_dir = app_name + "/ansible"
  roles_dir = ansible_dir + "/roles"

  if arg_vars.get('example_app') == 'beginner':
    print_ok_pending("Cloning beginner playbook via Git. Streaming Git output")
    call(["git", "clone", "https://github.com/onyx-platform/engraver-beginner-example.git", app_name])
    drop_git(app_name)
    print_done("Finished cloning example.")
  else:
    print_ok_pending("Invoking Leiningen and streaming its output")
    call(["lein", "new", "onyx-app", app_name, "+docker"])
    print_done("Finished executing Leiningen.")
  print("")

  print_ok_pending("Initializing .engraver folders")
  call(["mkdir", "-p", (app_name + "/.engraver")])
  call(["touch", (app_name + "/.engraver/config.json")])
  print_done("Finished .engraver folder initialization.")
  print("")

  print_ok_pending("Creating new Ansible playbook. Streaming Ansible output")
  call(["ansible-galaxy", "init", ansible_dir])
  call(["cp", resource_filename(__name__, "ansible_template/ansible.cfg"), ansible_dir])
  call(["cp", resource_filename(__name__, "ansible_template/refresh_cache.yml"), ansible_dir])
  print_done("Finished executing Ansible.")
  print("")

  print_ok_pending("Updating .gitignore for Engraver files")
  call("echo '.engraver/clusters/*' >> " + app_name + "/.gitignore", shell=True)
  call("echo 'ansible/machines_remove.yml' >> " + app_name + "/.gitignore", shell=True)
  call("echo 'ansible/cluster_remove.yml' >> " + app_name + "/.gitignore", shell=True)
  call("echo 'ansible/job_submit.yml' >> " + app_name + "/.gitignore", shell=True)
  call("echo 'ansible/job_kill.yml' >> " + app_name + "/.gitignore", shell=True)
  print_done("Finished updating .gitignore")
  print("")
  
  print_ok_pending("Cloning Ansible AWS playbook via Git. Streaming Git output")
  path = roles_dir + "/aws"
  call(["git", "clone", "https://github.com/onyx-platform/engraver-aws.git", path])
  drop_git(path)
  print_done("Finished cloning playbook.")
  print("")

  print_ok_pending("Cloning Ansible Docker playbook via Git. Streaming Git output")
  path = roles_dir + "/docker"
  call(["git", "clone", "https://github.com/onyx-platform/engraver-docker.git", path])
  drop_git(path)
  print_done("Finished cloning playbook.")
  print("")

  print_ok_pending("Cloning Ansible ZooKeeper playbook via Git. Streaming Git output")
  path = roles_dir + "/zookeeper"
  call(["git", "clone", "https://github.com/onyx-platform/engraver-zookeeper.git", path])
  drop_git(path)
  print_done("Finished cloning playbook.")
  print("")

  print_ok_pending("Cloning Ansible BookKeeper playbook via Git. Streaming Git output")
  path = roles_dir + "/bookkeeper"
  call(["git", "clone", "https://github.com/onyx-platform/engraver-bookkeeper.git", path])
  drop_git(path)
  print_done("Finished cloning playbook.")
  print("")

  print_ok_pending("Cloning Ansible Kafka playbook via Git. Streaming Git output")
  path = roles_dir + "/kafka"
  call(["git", "clone", "https://github.com/onyx-platform/engraver-kafka.git", path])
  drop_git(path)
  print_done("Finished cloning playbook.")
  print("")

  print_ok_pending("Cloning Ansible Onyx playbook via Git. Streaming Git output")
  path = roles_dir + "/onyx"
  call(["git", "clone", "https://github.com/onyx-platform/engraver-onyx.git", path])
  drop_git(path)
  print_done("Finished cloning playbook.")
  print("")

  print_ok_pending("Initializing Ansible vars directories")
  call(["mkdir", "-p", (ansible_dir + "/group_vars")])
  call(["mkdir", "-p", (ansible_dir + "/vars/cluster_vars")])
  print_done("Finished Ansible vars directory creation.")
  print("")
