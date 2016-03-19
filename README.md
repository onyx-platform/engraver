# Engraver

Engraver is command-line tool for managing and deploying Onyx clusters.

### What does it offer?

- A full application template, preloaded with best practices and design idioms
- Automatic cluster provisioning to a cloud environment
- Network security locked down by default
- High availability configured by default
- Containerized, preconfigured images of common services
- Automatic security group adjustment when services are added
- Log streaming to the developer machine
- Multi-tenancy as a first class concept
- Seamless scale up/down

### Installation

Available via Pip:

```
$ pip install engraver
```

#### Dependencies

To run Engraver, you will need:

- Python >= 2.7.8
- Java 8
- [Leiningen](http://leiningen.org/)
- [Ansible](http://docs.ansible.com/ansible/intro_installation.html#latest-releases-via-pip)
- [Docker](https://docs.docker.com/engine/installation/)
- [An AWS account](http://aws.amazon.com/)
- [A DockerHub account](https://hub.docker.com/)

### Summary

Engraver is a tool for managing Onyx cluster infrastructure. Unlike other platforms such as Spark and Hadoop, Onyx does not embed a feature for application deployment. The design decision to omit deployment is intentional since it lets application authors choose how and when to deploy application code instead of being forced to opt into a predetermined strategy.

There is a fair amount of overlap, however, between the deployment techniques for many teams that run Onyx in clustered, production environments. Engraver is a tool that unifies deployment code and makes a handful of opinionated decisions for the sake of making it easier to run Onyx in the cloud. Engraver itself is a Python based tool that wraps Ansible. We designed Engraver to make it friendly for getting started on using Onyx without knowing Ansible, but you're encouraged to learn Ansible along the way to make your Onyx deployment customized to your needs.

If you disagree with our set up of Ansible out of the box, that's fine. If you know enough about configuration management to take issue with the set up, you're in the category of developers that's advanced enough to not need Engraver. For everyone else, we've built Engraver to be a springboard into production, and as something that can be used for serious deployments.

Engraver has a small set of commands that are built to guide your engineering from initial design all the way into production:

<p align="center">
  <img width="60%" src="https://rawgit.com/onyx-platform/engraver/master/doc/images/lifecycle.svg">
</p>

### Concepts

This is a glossary for all the concepts that we use in Engraver. Each term is briefly explained. See other sections of the documentation for more in-depth discussion.

Here's a quick visual:

<p align="center">
  <img width="70%" src="https://rawgit.com/onyx-platform/engraver/master/doc/images/concepts.svg">
</p>

#### Clusters

A cluster is a set of virtual machines that run inside an isolated network. Machines are constructed from machine profiles, and run services when they are active. A cluster is the highest level of deployment isolation in Engraver.

#### Machine Profiles

A machine profile is a specification of what services should run on a virtual machine, what the specifications of the virtual machine are, and how many virtual machines should be created. For example, a machine profile would specify what image its operating system will run, which data center it will run in, and what flavor of machine is desired. It would also declare that it needs some number of those machines - perhaps 3.

#### Services

Services are programs that run on virtual machines. Examples of services are ZooKeeper and Kafka. Services are *typically* expected to run inside containers, but this isn't a strict requirement.

#### Provisioning

Provisioning is the act of creating the infrastructure for the cluster (Virtual Private Cloud, virtual machines, and so far), installing services, and starting the services. Provisioning is idempotent. If you provision more than once, Engraver will attempt to bring the cluster to the desired state determined by what the machine profiles specify.

#### Deployment

Deployment is the process by which Engraver deploys Onyx applications to virtual machines. Running the deployment command through Engraver will clean and uberjar your application, create a Docker image, upload the image to DockHub, and pull it down on all machines running the "Onyx" service. A container will be started on each machine, and Onyx will begin running.

#### Jobs

Engraver jobs refer to Onyx jobs. When we *submit* or *kill* a job, we are specifically talking about Onyx jobs. Since Onyx divorces the notion of deployment from job submision, we have the flexibility of doing rolling deployment updates to the Onyx application while the job continues to run on the cluster.

#### Ansible

Engraver wraps the Python configuration management tool Ansible. Engraver is primarily responsible for generating Ansible files in the background while commands are executed. Engraver interprets user commands and maps them to Ansible YAML files. When a change is ready to be made to a cluster, Engraver turns around and invokes Ansible under the hood. Engraver allows full access to Ansible for users who know what they're doing and want a little more power. You can even pass arguments directly to Ansible for commands that support it with the `--ansible` switch.

### How it Works

Engraver is a wrapper around Ansible. Ansible is a terrific tool for deploying virtual machines into the cloud and provisioning them to run user applications. There is, however, a fair amount of work that remains for development teams that cannot be quickly solved by Ansible alone - such as locking down security, attaching persistent volumes, and configuring clustered services for high availability. Engraver aims to solve common dev-ops tasks, and Ansible's YAML-based protocol is a hand-in-glove fit.

We aim to automatically generate *as few files as possible*, thus minimizing the number of collisions that can happen as a result of checking files into version control across teams.

#### Generated Files

The following files are automatically generated, and should not be manually edited:

- `ansible/<cluster_id>.yml`
- `ansible/deployment.yml`
- `ansible/cluster_remove.yml`
- `ansible/machine_remove.yml`
- `ansible/job_submit.yml`
- `ansible/job_kill.yml`
- `.engraver/clusters/*`

The following files are automatically generated, and *may* be edited by hand:

- `ansible/<cluster_id>_post.yml`
- `ansible/group_vars/<cluster_id>.yml`
- `ansible/vars/cluster_vars/test/machine_profiles/<profile_id>.yml`

When commands are invoked, Engraver scans the generated files and builds up an in-memory representation for the specification of your cluster. The files are, in turn, passed to Ansible to create the desired cluster.

### Machine Profiles In-Depth

It's helpful to think of machine profiles as "cookie-cutters". Profiles are specifications for what a particular machine should look like when we provision it in the cloud, and how many we want. In the image below, the right side represents 3 different profiles (the "specification" portion). The left side represents the manifestation of those profiles when they are provisioned.

<p align="center">
  <img width="70%" src="https://rawgit.com/onyx-platform/engraver/master/doc/images/profiles.svg">
</p>

This example shows a total of *10* machines actively running:
- 6 of them belong to the Onyx Profile
- 1 of them belongs to the Monitoring Profile
- 3 of them belong to the Ingestion Profile

#### Preconfigured High Availability

All 6 of the Onyx Profile machines in the example are running ZooKeeper, BookKeeper, and Onyx. By default, Engraver is preconfigured for highly available. That is, there would be 6 nodes running as a single ZooKeeper cluster.

If the same service runs in two different profiles, *all* instances of that service will run as a single unit. If this isn't desired, the services can be deployed in two different Engraver clusters for full isolation.

#### Service Dependencies

Some services require that other services be provisioned beforehand. A service can express dependencies by adding a `service_dependencies` key to its `defaults/main.yml` Ansible role. The value of this key should be a sequence of services. For example, the Onyx service declares the following dependencies:

```
service_dependencies:
  - zookeeper
  - bookkeeper
```

This forces the ZooKeeper and BookKeeper services to be provisioned before Onyx is provisioned on a machine.

### FAQ

- Q: How do I run my own provisioning playbook?
- A: Edit the `ansible/<cluster_id>_post.yml` file and create an Ansible playbook. This playbook will be invoked after running `ansible/<cluster_id>.yml` during the `engraver cluster provision` command.

-----------------

- Q: How do I force services to be brought up in a particular order?
- A: Edit the `ansible/roles/<service>/defaults/main.yml` file and add a `service_dependencies` key, with value of an array of service names. The services for a profile will be brought up in a topologically sorted order.

-----------------

- Q: How do I change a machine profile after I've provisioned it?
- A: Create a new profile (`engraver machines new`), and remove the old one (`engraver machines remove`). Machine profiles are like cattle.

### Tutorial

This a short guide that explains each major piece of Engraver by walking through an example.

#### Initialization

To make a new Engraver project named `hello-world`, run:

```
$ engraver init hello-world --example-app beginner
```

The `init` command will invoke Leiningen and create a new Onyx application template. It will clone some other repositories from the OnyxPlatform GitHub account. The extra clones are used for standing up your cluster in a cloud environment. We ran this command with the `--example-app` switch. We currently have one preconfigured project that we'll use for demonstration purposes.

The example application that we're going to deploy has one input and one output stream - both through Kafka. The workflow that we built for this app accepts messages and applies a few basic string transformations before routing them to an output stream. Study the source folder and run the tests for a local, in-memory execution of the Onyx job.

#### Account Configuration

Before we *really* get rolling, you'll need to tell Engraver about yourself. In this guide, we'll use AWS:

```
$ engraver configure aws
```

Fill out the prompts to authenticate yourself with AWS. For the "ssh remote user" prompt, use "ubuntu". This is the user that we'll use for SSH connectivity on our cluster. By default, the machines in an Engraver cluster run an Ubuntu Linux Distro.

#### Cluster Management

Once you `cd` into the `hello-world` directory and get comfortable with the Onyx project, you can create a specification for a new cluster. Engraver lets you have as many clusters as you want. Let's make a cluster called `dev` in AWS:

```
$ engraver cluster new --provider aws --cluster-id dev
```

Running this command will generate some files, but it won't actually stand up anything in AWS yet. We can inspect our specification with:

```
$ engraver cluster describe
+--------------+----------------+-----------+-------------------+
| Cluster Name | Cloud Provider | Region    | Availability Zone |
+--------------+----------------+-----------+-------------------+
| dev          | AWS            | us-east-1 | us-east-1a        |
+--------------+----------------+-----------+-------------------+
```

Clusters are automatically provisioned into a default region and availability zone. You can configure both of these on the command line with switches to the `cluster new` command.

#### Machine Profiles and Services

When you create a new cluster, Engraver will automatically generate a default *machine profile*. A machine profile is the set of services that will run *each machine provisioned with that profile*, and how many machines are desired. Machine profiles are higher level than simple services since it lets you express multiple services being colocated on a single machine.

Engraver gives us a default profile when we create a new profile. What's in it?

```
$ engraver machines describe --cluster-id dev
+------------+----------+-----------------------------+---------------+
| Profile ID | Size     | Services                    | Desired Count |
+------------+----------+-----------------------------+---------------+
| default    | c4.large | zookeeper, bookkeeper, onyx |       3       |
+------------+----------+-----------------------------+---------------+
```

The default profile gives us 3 services. Our example uses Kafka for its input and output streams, so we'll need to either modify the default profile or create a new one. In this tutorial, we'll simply edit modify the default profile.

Edit the `ansible/vars/cluster_vars/dev/machine_profiles/default_profile.yml` file, relative to the root of your project. You should see the following content:

```
profile_id: default
ec2_image_id: ami-d05e75b8
ec2_instance_type: c4.large
n_machine_instances: 3
machine_services:
  - zookeeper
  - bookkeeper
  - onyx
```

Add "`- kafka`" at the bottom of the file, and save it. Then run the command to describe the cluster again. You'll see your changes reflected:

```
$ engraver machines describe --cluster-id dev
+------------+----------+------------------------------------+---------------+
| Profile ID | Size     | Services                           | Desired Count |
+------------+----------+------------------------------------+---------------+
| default    | c4.large | zookeeper, bookkeeper, kafka, onyx |       3       |
+------------+----------+------------------------------------+---------------+
```

By default, Engraver is ready to provision the `dev` cluster with `3` machines of the default profile. Each of those machines will run Onyx, ZooKeeper, Kafka, and BookKeeper. Since these services are provided by Engraver itself, we've already preconfigured them to be highly available out of the box. These machines will be EC2 instances of type `c4.large`.

Is anything running yet? No, but we can verify that:

```
$ engraver machines list --cluster-id dev
> Hint: Displaying cached contents. Refresh status with: engraver machines cache

> No cached contents found.
```

Oops! What's happened? Engraver caches knowledge about provisioned clusters locally in the `.engraver` folder (the cache shouldn't be checked into version control to avoid merge conflicts, and it is put into the `.gitignore` by default). Certain commands automatically update the local cache for you. Since we haven't run such a command yet, we'll need to update the cache ourselves:

```
$ engraver machines cache --cluster-id dev

... Some Ansible output ...

> Finished updating local cache. Displaying cluster:
+--+----+---------+-----------------+------------+
|  | ID | Profile | Public DNS Name | Private IP |
+--+----+---------+-----------------+------------+
+--+----+---------+-----------------+------------+
```

Sure enough, we don't have any machines yet because we haven't provisioned. We can try listing again:

```
$ engraver machines list --cluster-id dev
> Hint: Displaying cached contents. Refresh status with: engraver machines cache

+--+----+---------+-----------------+------------+
|  | ID | Profile | Public DNS Name | Private IP |
+--+----+---------+-----------------+------------+
+--+----+---------+-----------------+------------+
```

After we provision, the `.engraver/clusters/dev.json` file will have lots of details about the machines that were brought up.

#### Provisioning

Time to stand up our cluster in the cloud. Run the following command to spin up our 3-node cluster:

```
$ engraver cluster provision --cluster-id dev
```

You'll see a fair amount of Ansible output. If you run into any unexpected problems, you can add `--ansible='-vvvv'` to the end of that line - which will put Ansible into verbose mode. When you provision in AWS, Ansible will:

- Create a Virtual Private Cloud (VPC)
- Create EC2 instances as describe by each of your machine profiles
- Install the requested services

Running provision is *idempontent*. You can run it again safely and it will update your existing cluster to your specification, not make a brand new one.

Once provisioning finishes, we can check our local cache, which has been automatically refreshed:

```
$ engraver machines list --cluster-id dev
> Hint: Displaying cached contents. Refresh status with: engraver machines cache

+---+------------+---------+-------------------------------------------+-------------+
|   | ID         | Profile | Public DNS Name                           | Private IP  |
+---+------------+---------+-------------------------------------------+-------------+
| 1 | i-171be88c | default | ec2-52-90-230-216.compute-1.amazonaws.com | 172.0.1.196 |
| 2 | i-161be88d | default | ec2-52-201-249-47.compute-1.amazonaws.com | 172.0.1.195 |
| 3 | i-141be88f | default | ec2-54-175-197-45.compute-1.amazonaws.com | 172.0.1.197 |
+---+------------+---------+-------------------------------------------+-------------+
```

If you log into each machine, you'll notice that there's no `onyx` container running on the machine. The Onyx Ansible role did run as a part of provisioning, but didn't start it's container yet. Onyx is a *library*, and is therefore bundled as part of the user level application. The Onyx container will be started during the Application Deployment phase.

#### Log Streaming

Most of our cluster up and running, but it'd be nice to know what the heck is going on! Engraver can automatically stream logs from Docker containers onto your nachine. Our machine profile asked for 3 machines to all run ZooKeeper, so let's take a look:

```
$ engraver logs ec2-52-90-230-216.compute-1.amazonaws.com --cluster-id dev --service zookeeper
```

Log contents will be streamed into your local terminal. You can abort out of it using your OS-specific key combination. Note that log streaming will only work for services that declare a `<service-name>_container_name` var in the default values file of their Ansible playbook.

#### Application Deployment

Everything is in place to deploy our Onyx application. We're going to deploy our app as a container using Docker and DockerHub. Make sure you're authenticated to DockerHub with:

```
$ docker login
```

Then deploy with:

```
$ engraver deploy --via dockerhub --cluster-id dev --tenancy-id message-processor --dockerhub-username <your username> --n-peers 4
```

This command uberjars your application, creates a container image, pushes it to DockerHub, then pulls it down onto any machines in your cluster that run the `onyx` service. It will starts `4` peers on each machine under the tenancy `message-processor`. This is going to take a while for the first time, so you might want to grab a cup of coffee. The Docker image for your application is uploading its base image, which includes Java, plus its own uberjar. After your first push and pull to/from DockerHub, the base image will be cached on both DockerHub and the machines on your cluster - drastically cutting down on upload/download time thereafter.

Verify that Onyx is running by inspecting the logs:

```
$ engraver logs ec2-52-90-230-216.compute-1.amazonaws.com --cluster-id dev --service onyx
```

#### Job Submission

The Onyx peers are running inside containers on each of the 3 machines our cluster, but they don't have any work to do yet. Now we're going to submit the job to fire them up:

```
$ engraver job submit --cluster-id dev --tenancy-id message-processor --job-name sample
```

This will submit the `sample` job to any Onyx peers in the cluster running under the `message-processor` tenancy id. You should see some activity in your logs that your job has begun.

The job is running, but there's nothing writing data to the input stream. We'll do that by hand for this tutorial for ease of use by leveraging the Kafka console producer and consumer scripts:

For the producer:

```
# SSH into a machine running Kafka
$ ssh -i ~/.ssh/your-key.pem ubuntu@ec2-52-90-230-216.compute-1.amazonaws.com

# Get a shell in the Kafka container
$ docker exec -it kafka /bin/bash

# Export JMX_PORT to avoid port collisions.
# Sigh, I know. :/
$ export JMX_PORT=10400

$ bin/kafka-console-producer.sh --broker-list 127.0.0.1:9092 --topic input-stream
```

For the consumer:

```
$ ssh -i ~/.ssh/your-key.pem ubuntu@ec2-52-90-230-216.compute-1.amazonaws.com

# Get a shell in the Kafka container
$ docker exec -it kafka /bin/bash

# Export JMX_PORT to avoid port collisions.
# Sigh, I know. :/
$ export JMX_PORT=10400

# ZOOKEEPER_IP is available as an environment variable on this container
$ bin/kafka-console-consumer.sh --zookeeper $ZOOKEEPER_IP --topic input-stream
```

In the console producer, fire off a few EDN messages:

```
{:message "Hello world"}
{:message "Onyx is running!"}
{:message "Here's a really long message to trigger a different code path"}
```

You should see messages stream into the console consumer as writing data through the console producer.

#### Autoscaling

Is 3 machines not enough? Maybe it's too many? Let's scale down 1 node:

```
$ engraver machines scale --cluster-id dev --profile-id default 1
> Updated local Ansible playbook. Now run: engraver cluster provision
```

We've updated our profile. Let's verify:

```
$ engraver machines describe --cluster-id dev
+------------+----------+------------------------------------+---------------+
| Profile ID | Size     | Services                           | Desired Count |
+------------+----------+------------------------------------+---------------+
| default    | c4.large | zookeeper, bookkeeper, kafka, onyx |       1       |
+------------+----------+------------------------------------+---------------+
```

The desired count is `1`, which updated our location specification. Let's make it real by running provisioning:

```
$ engraver cluster provision --cluster-id dev
```

We can see that provisioning has spun our cluster down to 1 machine:

```
$ engraver machines list --cluster-id dev
> Hint: Displaying cached contents. Refresh status with: engraver machines cache

+---+------------+---------+-------------------------------------------+-------------+
|   | ID         | Profile | Public DNS Name                           | Private IP  |
+---+------------+---------+-------------------------------------------+-------------+
| 1 | i-171be88c | default | ec2-52-90-230-216.compute-1.amazonaws.com | 172.0.1.196 |
+---+------------+---------+-------------------------------------------+-------------+
```

#### Teardown

When you're down with this tutorial, you can tear everything down with:

```
$ engraver cluster teardown --cluster-id dev
```

This will delete all EC2 instances in your VPC, then delete the VPC entirely. Thanks for playing!

### License

Copyright © 2016 Distributed Masonry

Distributed under the Eclipse Public License
