# java9_kernel
An ipython kernel for java 9

## Expectation Setting
This is an experimental ipython kernel written with an experimental repl written for
a unreleased java version. Don't expect this to be production ready.

That being said. File issues and ill do my best.

##Requirements

Install [java9](http://www.oracle.com/technetwork/articles/java/ea-jsp-142245.html)

Find or build yourself a kulla.jar 

[Out of date build guide](http://www.jclarity.com/2015/04/15/java-9-repl-getting-started-guide/)

[This link has a link to the jar](http://mythoughtsjdk.blogspot.com/2015/04/playing-with-java-9-and-repl-ljc-oracle.html)

This kernel expects two environment variables defined

```
KULLA_HOME - The locaiton of kulla.jar

JAVA_9_HOME - like JAVA_HOME but pointing to a java 9 environment
```

##Installing the kernel

Assuming you have cloned the repo and got all the requirements above setup

edit kernel.json replacing PATH_TO_javakernel to the location of the javakernel directory
 
```
mkdir ~/.ipython/kernels/java/

cp <location of your edited kernel.json> ~/.ipython/kernels/java/
```

For example my kernel.json looks like this

```
{
 "argv": ["python3", "/Users/bachmann/Code/java9_kernel/javakernel",
          "-f", "{connection_file}"],
 "display_name": "Java 9",
 "language": "java"
}
```

If all worked you should be able to run the kernel

```
 ipython console --kernel java
Jupyter Console 4.0.2

[ZMQTerminalIPythonApp] Loading IPython extension: storemagic
java version "1.9.0-ea"
Java(TM) SE Runtime Environment (build 1.9.0-ea-b71)
Java HotSpot(TM) 64-Bit Server VM (build 1.9.0-ea-b71, mixed mode)

In [1]: System.out.println("OMG")
 System.out.println("OMG")
OMG
```

It should work in a notebook as well

![Notebook Screenshot](notebook.png?raw=true)