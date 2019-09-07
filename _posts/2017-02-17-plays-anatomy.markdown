---
title: "Play’s Anatomy"
layout: post
date: 2017-02-17 22:48
image: /assets/images/posts/anatomy.jpeg
headerImage: true
tag:
- java
- scala
- api
- microservices
category: blog
author: samreghenzi
description: Solving common microservice problems with Play Framework
---
# Play’s Anatomy

We are doctors… are we?

A few weeks ago I found myself in the uncomfortable position of choosing a new “framework” to expose services through HTTP protocol. Well it would be handy if it had some other features:

* JSON serialization / deserialization

* jwt authentication

* Async response

* Easy integration with an existing AKKA based solution

* Testing facility / Controller unit testing / Integration testing and a reasonable way to measure coverage

* Monitoring

* Deployable Heroku

I started my humble quest: some frameworks looks promising, other in their way to the void. One day I was chatting with a friend no slack about my disappointing findings and he told me
> # I’m sorry to say that you’d probably should you Play

I had my own experience with Play. It was version 1.x and for the time, a time in which it was all about full stack frameworks and monoliths, is was fun and productive. Later on, I gave version 2.0 a try but I was horrified: it was slow and buggy… and since then I heard a lot of negative comments on Play. But I also see it is widely used and often when you use something a lot, you find all the rough edges.

So I decided to give it a try. I wanted to start with a minimal project so, instead of following the “getting started tutorial” I cloned this repo with all the intentions to implement the above feature set.
When I imported in the IDE my newly created project and I had a look at the dependencies it had my face was like:

![Freely quoting “The Hobbit” (Bagginses? What is Bagginses?)](https://cdn-images-1.medium.com/max/2000/1*bM2nwuf6DGf89G_-Z3bArg.jpeg)*Freely quoting “The Hobbit” (Bagginses? What is Bagginses?)*

A gazillion of jar just to send “hello world” to a browser? I’m a sort of dependencies zealot but for a good reason: in the many years I spent on the JVM platform I realized that the more jars you have on the classpath the more it behave erratic, generating problems often associated with headaches and sleepless nights. I was about to close the IDE and write my own thing from scratch. But, just for the sake of curiosity, I start looking around. The “railesque” structure is sill there, but I learn after that you can switch to a more traditional sbt structure. The route file is optional as long as you define you route object, a standard approach in most of the scala frameworks I have worked with. The module system looks promising and it lost his horrible resemblance with the rails plugins systems that originally inspired it. Now modules are traits that plug in the application with the support of a runtime dependency injection. The default implementation is Google Juice. And this is the first of the many reasons a lot of people do not enjoy working with play. DI is a controversial topic, especially with scala…. Play is a very opinionated framework: most of the decisions has been already taken for you. This is why a lot of people don’t like it. I love minimalism in my tools, but I told to myself: this is the least interesting part of the solution, I just want a first class support to modern web features without going mad on low-level HTTP details. My problem with Play were the numerous many moving parts… so I tried to remove them, or at least to minimize the chance that they could get in my way.

## **Build Automation**

The most disturbing thing in past versions of play was that sbt was an option and not the standard. Now you can have a simple sbt build for your play project with a custom plugin. Just add your favorite plugins.

* **sbt-release:** I like to have different features in different releases

* **sbt-scoverage**: To check if something is missing

* **sbt-coveralls: **Is always nice to have fancy reports

I used these sbt plugins before and found them perfect for a short release pipeline. Even if this was a solo project I added Travis-ci support just to have a build pipeline as close as possible to a real one. This is a crucial part for me in the decision-making project. Build automation is something that drives your product/project to success or damnation really quickly (in both cases ).
JSON serialization / deserialization

## JSON serialization / deserialization

Play comes with his own JSON library, but I have a crush for Circe
[**circe**
*A JSON library for Scala powered by Cats*circe.github.io](https://circe.github.io/circe/)

It is fast and provides a very functional to do things. The good part is that being so popular there already is a play-circe integration! The best of both worlds!

    case class Bar(bar: Int)  
    case class Foo(foo: String, bar: Bar)  

    def get = Action { request =>    
        val foo = ...
        Ok(foo.asJson)  
    }

## JWT authentication

Again, due to the popularity of Play jwt-play is a pret aprote solution to my problem and it plugs in the request / authentication system already in place: to have the details of the current request in one of your controllers.. just read it!

        request.jwtSession.getAs[User]("user") 

No more messing around with keys, shared secrets, headers… if you are not in a hacking mood.

So far so good. But then I tried to add swagger support to my secured JSON controller. Long story short it was not supported by the official Swagger Play Integration. So I fixed it. I made a pull request…. and nothing happened. So I forked the repo and make my own bootleg release

    *resolvers *+= "sammyrulez" at "https://raw.githubusercontent.com/sammyrulez/my-maven-repo/master/"
    
    libraryDependencies ++= Seq("io.swagger" %% "swagger-play2" % "1.5.4-SNAPSHOT")

You are wellcome.

More on episode 2 …
