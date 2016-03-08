# Engraver

Engraver is command-line tool for managing and deploying Onyx clusters.

### What does it offer?

- A full application template, preloaded with best practices and design idioms
- Automatic cluster provisioning to a cloud environment
- Secure, highly available configurations out of the box
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
- [Boto](https://github.com/boto/boto#installation)
- [Ansible](http://docs.ansible.com/ansible/intro_installation.html#latest-releases-via-pip)
- [Docker](https://docs.docker.com/engine/installation/)
- [An AWS account](http://aws.amazon.com/)
- [A DockerHub account](https://hub.docker.com/)

### Summary

Engraver is a tool for managing Onyx cluster infrastructure. Unlike other platforms such as Spark and Hadoop, Onyx does not provide a means for application deployment. The design decision to omit deployment is intentional since it lets application authors choose how and when to deploy application code instead of being forced to opt into a predetermined strategy.

There is a fair amount of overlap, however, between the deployment techniques for many teams that run Onyx in clustered, production environments. Engraver is a tool that unifies deployment code and makes a handful of opinionated decisions for the sake of making it easier to run Onyx in the cloud. Engraver itself is a Python based tool that wraps Ansible. We designed Engraver to make it friendly for getting started on using Onyx without knowing Ansible, but you're encouraged to learn Ansible along the way to make your Onyx deployment customized to your needs.

If you disagree with our set up of Ansible out of the box, that's fine. If you know enough about configuration management to take issue with the set up, you're in the category of developers that's advanced enough to not need Engraver. For everyone else, we've built Engraver to be a springboard into production, and can be used for serious deployments.

### User Guide

This a short guide that explains each major piece of Engraver. You can skip down to the bottom of this README for the specification of every command, switch, and option in Engraver.

#### Initialization

To make a new Engraver project named `hello-world`, run:

```
$ engraver init hello-world
```

The `init` command will invoke Leiningen and create a new Onyx application template. It will clone some other repositories from the OnyxPlatform GitHub account. The extra clones are used for standing up your cluster in a cloud environment.

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

If you want to have a look for yourself, check out `.engraver/clusters/dev.json` to see the full machine cache.

#### Provisioning

#### Log Streaming

#### Application Deployment

#### Generated Files

### License

Copyright © 2016 Distributed Masonry

Distributed under the Eclipse Public License
