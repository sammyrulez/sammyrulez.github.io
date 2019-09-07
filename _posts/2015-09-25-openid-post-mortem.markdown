---
title: "OpenId: a postmortem"
layout: post
date: 2015-09-24 22:48
image: /assets/images/markdown.jpg
headerImage: false
tag:
- sso
- security
- api
category: blog
author: samreghenzi
description: Why openId did not got adopted everywhere
---
# OpenId: a postmortem

Some years ago I was a big fan of OpenID and tried to promote it in my various dev communities. It was a good solution to a problem that I knew enough fine. The single sign-on. Mandatory definition of SSO:
> Single sign-on (SSO) is a property of access control of multiple related, but independent software systems.
> With this property a user logs in with a single ID to gain access to a connected system or systems without being prompted for different usernames or passwords, or in some configurations seamlessly sign on at each system.

OpenID provides a clear answer to a as crucial as tedious aspect of the development process: authentication.

## POSTMORTEM:

First of all OpenID is not dead. In particular contexts I would use ir again. But what went wrong?

Technically speaking using OpenID in your application is not particularly complex. Libraries are available for all programming languages ​​and for all mainstream web frameworks. Realizing a OpenID provider is rather complicated through.

Choosing an OpenID provider (or more than one) has not been easy. Although one of the strengths of the solution is to have a URI and delegate identity management to a provider (so you can change without having to change URI),this process is not within the reach of the average user. This brings us to the third point

OpenId is only for “geeks / nerds / dev”: the concept of distributed identity is beyond the comprehension of the average user. I do not think, as I have heard, that the authentication is a “self-imposed” problem (it is like saying that hunger is a self-imposed problem: everyone has to eat!)

OpenId haven’t a clear, simple and universally accepted mechanism for user details exchange between client application and provider. This forces the client app to ask for the data again during the “registration” process and undermines the fact of having a centralized identity manager.

Oauth and the apocalypse of social networks: all of the above problems have been solved with the advent of social networks and the exposure of its API with Oauth upon them. The famous “Facebook connect” or “Sign is with Twitter”. The client application could access the potential user data with a few of clicks, with the help an “authority” perceived as safe/secure . As a bonus there is also to be able to put his nose in the activity of its members on the above company. Win win situation.

The two details that amaze me to this last point is that Oauth born as a system of authorization and authentication, and that many developers think that OpenID is a particular version / dialect / library Oauth.

The most absurd part of the whole thing is that at some point OpenId had started to have some popularity.

Microsoft, Google, had begun to act as providers, huge sites like StackOverflow had started using it with [some success](http://blog.stackoverflow.com/2010/04/openid-one-year-later/)

I think that OpenID, although it is not a technology dead, has no longer the chance to reach enought momentum to become the “go to” solution for single sign-on. Definitely a missed opportunity. Who is to blame? Perhaps all of us ( just a bit) and no one in particular. I just hope that solutions emerge to orchestrate better authorization processes through Oauth that put to a more responsible use of data and integration between the web-apps.
