---
title: "The post I link when someone tells me that Java sucks"
layout: post
date: 2016-11-22 22:48
image: /assets/images/posts/java-skull.png
headerImage: true
tag:
- java
- scala
- api
category: blog
author: samreghenzi
description: it doesn't
---
# The post I link when someone tells me that Java sucks



I had the chance to use other languages as well, but I spent the most part on Java or on JVM based languages. I had the chance to use also other languages (python to name one I absolutely love).

In all these years I had to handle a lot of “Java sucks” conversations with people religiously in love with the language of the moment. So I resolute to write this post and link it whenever … a shit conversation that happens. I will present my point in favor of Java/ JVM based environment with a big bold disclaimer:

**I DO NOT think that Java is the best language in the world and I love to learn new stuff. At the time of writing, *for the stuff I’m working on* is just the best (IMHO) Option available.**

These are the top 5 reasons people usually try to persuade me that Java sucks

* **Java is slow**: this is plain wrong. Big data solutions ( spark, hadoop ) are all built on the JVM. Speaking of internet performance, Java solutions are the most performant ones after native engines: here you can check some [data](https://www.techempower.com/benchmarks/#section=data-r12&hw=peak&test=fortune&l=nvnl). Maybe it was true in the past ( 10 years ago). Maybe GUI application built in Java is slower than a native one, but it is oblivious since native will always outrun a virtual environment.

* **Java is verbose:** What are we talking about here? The lack of syntactic sugar? The historical tradition to make all properties private than accessed with getter/setter methods? In modern Java ( 1.8 ) you can write pretty concise code with static imports to build quick DSL, annotation and annotation parser to build meta programming stuff, closures. There are historical reasons for some of the design choices. Let me quote [this answer on Quora](https://www.quora.com/Why-is-Java-so-verbose): *Why is java so verbose?*
> The philosophy behind Java is evident in that it insists on making the programmer explicitly type out what they mean rather than providing syntactic sugar. For example, to create a derived class you use the word “extends” rather than “:” as in C++. There is no user-defined operator overloading. Naming conventions in Java result in very long names. Etc. Etc. The idea was to make a language which prevented novice mistakes and abuse. Java was basically a language designed by experts for non-experts

* **Java is an old language ( or ”Java is the new Cobol”):** Java 1.8 has all the features of a statically typed Object Oriented features plus some Functional programming features. That said is also a very successful language so there is a lot of legacy code around, a lot of bad code ( because the more a language is used the more bad code is produced: more on this later). Long story short: yes you can write modern code with Java. There is a reason you need a dynamically typed language? Use Groovy. Want A Functional Programming language, first of its kind and most used in the industry? Try Scala! ( I love it!). The claim “startups do not use it” is plain false.
[**Why did we choose Scala? · Real-time analytics on complex data streams — Valo**
*Posted Aug 10, 2016 by Valo Dev in Big Data and Scala Share in It is undeniably the case in IT that any new product, no…*www.valo.io](https://www.valo.io/2016/08/10/why-did-we-choose-scala/)
[**What kind of companies use Java as their primary language in software development?**
*Answer (1 of 12): While Facebook may use C++ and PHP, they also use Java extensively. Java is the language of business…*www.quora.com](https://www.quora.com/What-kind-of-companies-use-Java-as-their-primary-language-in-software-development)

[How PayPal Scaled To Billions Of Transactions Daily Using Just 8VMs](http://highscalability.com/blog/2016/8/15/how-paypal-scaled-to-billions-of-transactions-daily-using-ju.html)

[What startups or tech companies are using Scala?](https://www.quora.com/What-startups-or-tech-companies-are-using-Scala)

* **Framework X / Java EE is over-engineered: **maybe… don’t use it. There are plenty of options. Java EE is a very broad variety of technologies and opensource frameworks that offer alternatives pops up every even day. Probably the real problem with Java is that products ( from commercial application source to open source lib) became feature bloated in time. I think because most of them are bound to enterprise development and that kind of market ( which I know pretty well) is a curse with the “adding features” madness. And then poor design also happens. I saw it with projects like Hibernate: I used it since version 1.28 and I witnessed it becoming a huge juggernaut entangled with hundreds of dependencies. When this happens probably people think it Java fault … it’s not.

* **Java is not open source / backed by corporations with evil intents: **maybe you lived writing PHP scripts in a mobile house with limited internet connection for the last 10 years. In that case, have a look [here](http://openjdk.java.net) to the OPEN JDK.

If you want more details on the Java/JVM ecosystem to have a look at this article series by Geert Bevin
[**10 Reasons Why Java Rocks: Part I | zeroturnaround.com**
*When I was away from Java to work on the software of the Eigenharp instruments, I had to develop cross-platform real…*zeroturnaround.com](http://zeroturnaround.com/rebellabs/10-reasons-why-java-now-rocks-more-than-ever-part-1-the-java-compiler/)

This is going to be a “work in progress“ blog post since I think people will find always new reasons to rant.
