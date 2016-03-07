#!/usr/bin/env python

import json
import os

from subprocess import check_output, call

from ansible import invoke_ansible
from colors import bcolors

def deploy(arg_vars, project_root):
  with open(project_root + "/.engraver/config.json", "r") as data_file:    
    organization = json.load(data_file)['organization']

  version = check_output(["lein", "project-version"]).strip()
  project_name = os.path.relpath(project_root, "..")
  image = organization + "/" + project_name + ":" + version

  print(bcolors.OKBLUE + "> Creating an uberjar for your project. Streaming Leiningen output ..." + bcolors.ENDC)
  call(["lein", "uberjar"])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished creating the uberjar." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Creating a container. Streaming Docker output ..." + bcolors.ENDC)
  call(["docker", "build", "-t", image, project_root])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished building container image " + image + "." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Turning image into a tar file ..." + bcolors.ENDC)
  call(["docker", "save", "-o", "target/" + project_name + "-" + version + ".tar.gz", image])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished tar'ing image." + bcolors.ENDC)

  print(bcolors.OKBLUE + "> Running Ansible deployment playbook. Streaming Ansible output ..." + bcolors.ENDC)
  invoke_ansible(arg_vars, project_root, arg_vars['cluster_id'] + ".yml",
                 {"onyx_docker_image": image})
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished running Ansible. Onyx has been successfully deployed." + bcolors.ENDC)
