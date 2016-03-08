# Engraver

Engraver is command-line tool for managing and deploying Onyx clusters.

### What does it offer?

- A full application template, preloaded with best practices and design idioms
- Automatic cluster provisioning to a cloud environment
- Secure, highly available configurations out of the box
- Containerized, preconfigured images of common services
- Log streaming to the developer machine
- Seemless scale up/down

### Installation

Available via Pip:

```
$ pip install engraver
```

### Summary

Engraver is a tool for managing Onyx cluster infrastructure. Unlike other platforms such as Spark and Hadoop, Onyx does not provide a means for application deployment. The design decision to omit deployment is intentional since it lets application authors choose how and when to deploy application code instead of being forced to opt into a predetermined strategy.

There is a fair amount of overlap, however, between the deployment techniques for many teams that run Onyx in clustered, production environments. Engraver is a tool that unifies deployment code and makes a handful of opinionated decisions for the sake of making it easier to run Onyx in the cloud. Engraver itself is a Python based tool that wraps Ansible. We designed Engraver to make it friendly for getting started on using Onyx without knowing Ansible, but you're encouraged to learn Ansible along the way to make your Onyx deployment customized to your needs.

If you disagree with our set up of Ansible out of the box, that's fine. If you know enough about configuration management to take issue with the set up, you're in the category of developers that's advanced enough to not need Engraver. For everyone else, we've built Engraver to be a springboard into production, and can be used for serious deployments.

### User Guide

#### Initialization

#### Cluster Management

#### Services

#### Machine Management

#### Log Streaming

#### Application Deployment

### License

Copyright © 2016 Distributed Masonry

Distributed under the Eclipse Public License
