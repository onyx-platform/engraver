#!/usr/bin/env python

import json
import os

from subprocess import check_output, call

from ansible import invoke_ansible, refresh_deployment_playbook
from colors import bcolors

def deploy(arg_vars, project_root):
  organization = arg_vars['dockerhub_username']
  version = check_output(["lein", "project-version"]).strip()
  project_name = os.path.relpath(project_root, "..")
  image = organization + "/" + project_name + ":" + version

  if not arg_vars.get('skip_uberjar'):
    print(bcolors.OKBLUE + "> Creating an uberjar for your project. Streaming Leiningen output ..." + bcolors.ENDC)
    call(["lein", "uberjar"])
    print(bcolors.OKBLUE + bcolors.BOLD + "> Finished creating the uberjar." + bcolors.ENDC)
    print("")

  print(bcolors.OKBLUE + "> Creating a container. Streaming Docker output ..." + bcolors.ENDC)
  call(["docker", "build", "-t", image, project_root])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished building container image " + image + "." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Uploading image to DockerHub ..." + bcolors.ENDC)
  call(["docker", "push", image])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished pushing image." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Updating Ansible deployment playbook ..." + bcolors.ENDC)
  refresh_deployment_playbook(arg_vars, project_root)
  print(bcolors.OKBLUE + "> Ansible playbook update complete." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Running Ansible deployment playbook. Streaming Ansible output ..." + bcolors.ENDC)
  invoke_ansible(arg_vars, project_root, "deploy.yml", {"onyx_docker_image": image,
                                                        "onyx_tenancy_id": arg_vars['tenancy_id'],
                                                        "onyx_n_peers": arg_vars['n_peers']})
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished running Ansible. Onyx has been successfully deployed." + bcolors.ENDC)
