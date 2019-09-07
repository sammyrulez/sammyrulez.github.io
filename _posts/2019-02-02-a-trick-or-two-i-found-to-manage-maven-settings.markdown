---
title: "A trick or two I found to manage maven settings"
layout: post
date: 2019-02-02 22:48
tag:
- java
- maven
- devops
category: blog
author: samreghenzi
description:  
---
# A trick or two I found to manage maven settings



A few weeks ago I was setting up a minimal Continuous Integration solution based on Maven running on Bitbucket pipelines. To frame the problem lets just say it was a git mono-repo with the sources of multiple artifacts. Some of these artifacts where runnable applications, but others where client libraries that I had to deploy in a private maven repository. Now I run into a security issue and a moral problem: maven stores credentials to access private repository in the settings.xml configuration file. Although everybody uses a global/ system-wide settings.xml is also possible to override with a local one using the -s cli switch. According to maven’s documentation is not possible to pass repository credentials from the command line. Now I surely don’t want to commit a file with my private maven repository credentials in it. I don’t even want to commit a settings.xml file into my git repo just for the sake of the Continuous Integration. Many CI product asks for a configuration file in the root repository with the description of the actions flow for the build (bitbucket-pipelines.yml): this is the necessary evil and the maximum level of intrusion I can stand in my projects.
So I used the environment variable substitution feature of Maven to solve the first issue. In a custom settings.xml file, I defined the server entries for my private repo, but I put just placeholders for environment variables.

<iframe src="https://medium.com/media/af936afc41822c087c98df7e36d3313d" frameborder=0></iframe>

Then I defined my.repo.user and my.repo.password as environment variables in Bitbucket pipeline system.

But still I had a rogue settings xml in my git repo. To get rid of that I thought that I could embed it in the bitbucket-pipelines.yml file, which is the only file I want to maintain for the CI stuff. So I base64 encoded it and I added a step in the build to decode it.

<iframe src="https://medium.com/media/fefb27121b84cf87acdc06eb0c795dd2" frameborder=0></iframe>

Et voilà a clean and secure solution to deploy my artifacts in a private repo from bitbucket ( or similar CI products)
