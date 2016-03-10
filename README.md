# Engraver

Engraver is command-line tool for managing and deploying Onyx clusters.

### What does it offer?

- A full application template, preloaded with best practices and design idioms
- Automatic cluster provisioning to a cloud environment
- Network security locked down by default
- High availability configured by default
- Containerized, preconfigured images of common services
- Log streaming to the developer machine
- Multi-tenancy as a first class concept
- Seemless scale up/down

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

Engraver is a tool for managing Onyx cluster infrastructure. Unlike other platforms such as Spark and Hadoop, Onyx does not provide a means for application deployment. The design decision to omit deployment is intentional since it lets application authors choose how and when to deploy application code instead of being forced to opt into a predetermined strategy.

There is a fair amount of overlap, however, between the deployment techniques for many teams that run Onyx in clustered, production environments. Engraver is a tool that unifies deployment code and makes a handful of opinionated decisions for the sake of making it easier to run Onyx in the cloud. Engraver itself is a Python based tool that wraps Ansible. We designed Engraver to make it friendly for getting started on using Onyx without knowing Ansible, but you're encouraged to learn Ansible along the way to make your Onyx deployment customized to your needs.

If you disagree with our set up of Ansible out of the box, that's fine. If you know enough about configuration management to take issue with the set up, you're in the category of developers that's advanced enough to not need Engraver. For everyone else, we've built Engraver to be a springboard into production, and can be used for serious deployments.

### User Guide

This a short guide that explains each major piece of Engraver by walking through an example.

#### Initialization

To make a new Engraver project named `hello-world`, run:

```
$ engraver init hello-world
```

The `init` command will invoke Leiningen and create a new Onyx application template. It will clone some other repositories from the OnyxPlatform GitHub account. The extra clones are used for standing up your cluster in a cloud environment.

#### Account Configuration

Before we *really* get rolling, you'll need to tell Engraver about yourself. In this guide, we'll use AWS:

```
$ engraver configure aws
```

Fill out the prompts to authenticate yourself with AWS.

#### Cluster Management

Once you `cd` into the `hello-world` directory and get comfortable with the Onyx project, you create a specification for a new cluster. Engrave lets you have as many clusters as you want. Let's make a cluster called `dev` in AWS:

```
$ engraver cluster new --provider aws --cluster-id dev
```

Running this command will generate some files, but it won't actually stand up anything in AWS yet. We can inspect our specification specification with:

```
$ engraver cluster describe
+--------------+----------------+-----------+-------------------+
| Cluster Name | Cloud Provider | Region    | Availability Zone |
+--------------+----------------+-----------+-------------------+
| dev          | AWS            | us-east-1 | us-east-1b        |
+--------------+----------------+-----------+-------------------+
```

Clusters are automatically provisioned into a default region and availability zone. You can configure both of these on the command line with switches to the `cluster new` command.

#### Machine Profiles and Services

When you create a new cluster, Engraver will automatically generate a default *machine profile*. A machine profile is the set of services that will run on a machine, and how many machines are desired. Machine profiles are higher level than simple services since it lets you express multiple services being colocated on a single machine.

Engraver gives us a default profile. What's in it?

```
$ engraver machines describe --cluster-id dev
+------------+----------+-----------------------------+---------------+
| Profile ID | Size     | Services                    | Desired Count |
+------------+----------+-----------------------------+---------------+
| default    | c4.large | zookeeper, bookkeeper, onyx |       3       |
+------------+----------+-----------------------------+---------------+
```

By default, Engraver is ready to provision the `dev` cluster with `3` machines. Each of those machines will run Onyx, ZooKeeper, and BookKeeper. Since these services are provided by Engraver itself, we're preconfigured them to be highly available out of the box. These machines will be EC2 instances of type `c4.large`.

Is anything running yet? No, but we can verify that:

```
$ engraver machines list --cluster-id dev
> Hint: Displaying cached contents. Refresh status with: engraver machines cache

> No cached contents found.
```

Oops! What's happened? Engraver caches knowledge about provisioned clusters locally in the `.engraver` folder (the cache shouldn't be checked into version control to avoid merge conflicts). Certain commands automatically update the local cache for you. Since we haven't run such a command yet, we'll need to update the cache ourselves:

```
$ engraver machines cache --cluster-id dev

... Some Ansible output ...

> Finished updating local cache. Displaying cluster:
+--+----+---------+-----------------+------------+
|  | ID | Profile | Public DNS Name | Private IP |
+--+----+---------+-----------------+------------+
+--+----+---------+-----------------+------------+
```

Sure enough, we don't have any machines yet. Now we can try listing again:

```
$ engraver machines list --cluster-id dev
> Hint: Displaying cached contents. Refresh status with: engraver machines cache

+--+----+---------+-----------------+------------+
|  | ID | Profile | Public DNS Name | Private IP |
+--+----+---------+-----------------+------------+
+--+----+---------+-----------------+------------+
```

After we provision machines, you can check out `.engraver/clusters/dev.json` to see the full machine cache.

#### Provisioning

Time to provision our cluster in the cloud. Run the following command to spin up our 3-node cluster:

```
$ engraver cluster provision --cluster-id dev
```

You'll see a fair amount of Ansible output. When you provision in AWS, Ansible will:

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

#### Log Streaming

With our cluster up and running, it'd be nice to know what the heck is going on! Engraver can automatically stream logs from Docker containers onto your nachine. Our machine profile asked for 3 machines to all run ZooKeeper, so let's take a look:

```
$ engraver logs --cluster-id dev --service zookeeper ec2-52-90-230-216.compute-1.amazonaws.com
```

A stream of log contents will be played into your terminal. You can abort out of it using your OS-specific key combination. Note that log streaming will only work for services that declare a `container_name` var in the default values file of their Ansible playbook.

#### Autoscaling

Is 3 machines not enough? Maybe it's too many? Let's scale down 1 node:

```
$ engraver machines scale --cluster-id dev --profile-id default 1
> Updated local Ansible playbook. Now run: engraver cluster provision
```

We've updated our profile. Let's verify:

```
$ engraver machines describe --cluster-id dev
+------------+----------+-----------------------------+---------------+
| Profile ID | Size     | Services                    | Desired Count |
+------------+----------+-----------------------------+---------------+
| default    | c4.large | zookeeper, bookkeeper, onyx |       1       |
+------------+----------+-----------------------------+---------------+
```

Desired count is `1`. Let's make it happen by provisioning!

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

#### Application Deployment

Everything is in place to deploy our application. We're going to deploy our application as a container using Docker and DockerHub. Make sure you're authenticated to DockerHub with:

```
$ docker login
```

Then deploy with:

```
$ engraver deploy --via dockerhub --cluster-id dev --tenancy-id mdrogalis --dockerhub-username michaeldrogalis --n-peers 4
```

The above command uberjars your application, creates a container image, pushes it to DockerHub, then pulls it down onto any machines in your cluster that run the "Onyx" service. It will starts `4` peers on each machine. This is going to take a while for the first time, so you might want to grab a cup of coffee. The Docker image for your application is uploading its base image, which includes Java, plus its own uberjar. After your first push and pull to/from DockerHub, the base image will be cached on both DockerHub and the machines on your cluster - drastically cutting down on upload/download time thereafter.

#### Teardown

When you're down with this tutorial, you can tear everything down with:

```
$ engraver cluster teardown --cluster-id dev
```

This will delete all EC2 instances in your VPC, then delete the VPC entirely.

#### Generated Files

### License

Copyright © 2016 Distributed Masonry

Distributed under the Eclipse Public License
