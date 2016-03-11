#!/usr/bin/env python

from colors import bcolors
from subprocess import call

from ansible import refresh_submit_playbook, refresh_kill_playbook

def job_submit(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Invoking Ansible and streaming its output ..." + bcolors.ENDC)
  refresh_submit_playbook(arg_vars, project_root)
  invoke_ansible(arg_vars, project_root, "job_submit.yml",
                 {"onyx_job_name": "job_name"})
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished running Ansible." + bcolors.ENDC)

def job_kill(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Invoking Ansible and streaming its output ..." + bcolors.ENDC)
  refresh_kill_playbook(arg_vars, project_root)
  invoke_ansible(arg_vars, project_root, "job_kill.yml",
                 {"onyx_job_id" : "job_id"})
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished running Ansible." + bcolors.ENDC)
