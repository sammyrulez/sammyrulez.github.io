---
title: "Plays Anatomy: Episode 2"
layout: post
date: 2017-04-17 22:48
headerImage: false
tag:
- playframework
- scala
- api
category: blog
author: samreghenzi
description: Episode 2
---
# The post I link when someone tells me that Java sucks
# Plays Anatomy: Episode 2

Previously on Plays Anatomy….

[Take a look](https://medium.com/@SammyRulez/plays-anatomy-8c0fc865ef37) at part one in case you miss it.

You find ALL the code on my Github repo
[**sammyrulez/minimal-play2**
*minimal-play2 - minimal rest service protorype*github.com](https://github.com/sammyrulez/minimal-play2)

Next on my checklist of desirable features were async response and 
easy integration with an existing AKKA based solution. Play comes with bounded AKKA support. This is a strongly opinionated choice, but in my case, works just fine with the type of systems I would like to integrate.A Play application defines an actor system at start time, add it to the IoC container and it can be used by other modules. This actor system follows the application life-cycle (Automagically). Then you can just ask the system for an actor ad use it as a gateway to other components of the Akka system ( even a distributed one). Having Akka support out of the box without hustle and bustle has benne a huge plus since this is something I spent a lot of time with little satisfaction. You can return Future from an actor response mapping it in a HttpResponse with an “Action.async”

def index = Action.async {
 val futureInt = scala.concurrent.Future { intensiveComputation() }
 futureInt.map(i => Ok(“Got result: “ + i))
}

Akka HTTP is one of the options for the embedded HTTP server in Play project ( the other is Netty). So you see the two frameworks are very bonded together, which is not a good thing by itself, but if you already have chosen Akka as asynchronous actor support, then this bound becomes a positive aspect. 
 I found a very good example at [http://loicdescotte.github.io/posts/play25-akka-streams/](http://loicdescotte.github.io/posts/play25-akka-streams/) that explains how to integrate Akka Streams in play ( if this is your thing).

Testing… testing helps me sleeping better. I don’t mean testing is boring! It make me feel safe: make me feel quite sure that what I’m going to deploy is, at least, technically correct.

Play framework offers a variety of testing facilities, provisioning tools for bot unit and integration testing. Everything is really straight forward and you can find everything in the documentation.

On top of standard Play’s tool, I added **scoverage** and **coveralls** to track and publish testing coverage of my project. They have both sbt plugins to integrate smoothly in the build process and you can make Travis build fail if the coverage drop below a certain level or is worst than the previous build. This is particularly useful when you have to decide to accept a merge request or not. If the new feature or fix is not supported by additional test, you can make the build fail automatically.

For **monitoring **I tried **“[markscheider](https://github.com/zalando-incubator/markscheider)” **which is a tool by Zalando.
> The name stems from the german mining term [Markscheider](https://de.wikipedia.org/wiki/Markscheider), which was a land surveyor who was responsible for mapping of the mine.

For monitoring, I tried “markscheider” which is a tool by Zalando.
The name stems from the german mining term Markscheider, which was a land surveyor who was responsible for mapping of the mine.

It is a Play module that integrates dropwizard Metrics ( the only good part in dropwizard… IMHO ) The metrics are created in a way that is compatible with ZMON.

Probably the best tool for monitoring is Kamon but it requires backend integration with publishing services ( like *new relic, datadog* or you own hosted solution ) and it went a bit beyond the scope of my experiment.

And then **deploy all the things**! I find Heroku a convenient platform for this kind of experiments. There is a specific guide on Heroku documentation site to deploy Play applications but this is a fast crash course.

![Heroku supports Play applications](https://cdn-images-1.medium.com/max/4656/1*YFUQ5WN5b9qSWltvjB8CIg.png)*Heroku supports Play applications*

Play has a special **stage sbt task** to build a uber jar, an executable archive with all the classes required to run your application. You just have to add in the root of your git repo a Proc file that defines how to startup your process
[**sammyrulez/minimal-play2**
*minimal-play2 - minimal rest service protorype*github.com](https://github.com/sammyrulez/minimal-play2/blob/master/Procfile)

    web: target/universal/stage/bin/minimal-play2 -Dhttp.port=${PORT} -Dplay.crypto.secret=${APPLICATION_SECRET}

the ${xxx} are variables:

* ${PORT} is a Heroku variable with the port the app should bind to be exposed by their reverse proxy

* ${APPLICATION_SECRET} is a user define property that you can form Heroku console… a handy way to pass “secret” values (is apikey, oAuth credentials etc ) to you app without storing them in config files.

So now we are up and running!

Open the “[home page](http://minimal-play2.herokuapp.com)”, thake note of the user token and try the [api](http://minimal-play2.herokuapp.com/webjars/swagger-ui/2.2.6/index.html?url=http://minimal-play2.herokuapp.com/swagger.json) with Swagger . Have fun!
