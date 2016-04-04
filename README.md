About
---------
Database web interface server based on Docker, Apache2 and web2py framework.

HOW TO GET STARTED
--------------------
This package does not ship with a complete web2py framework. It only ships with the web development part (db/controllers/views), 
aka web2py 'app', located under ./web2py/applications/.  On first clone from git repository you fetch the latest web2py framework
by executing the command 

```
 $ ./get_latest_web2py.sh
```

You re-run this command at a later time if newer versions of web2py become available. Updating web2py should not cause problems because
the framework tries to be strongly backwards compatible.

It is necessary to create an admin password to be able to log in securely using the admin web2py admin interface 
under https://mysite/admin .  Create your admin password by executing the command

```
 $ ./create_admin_passw.sh
```

You can now compile the docker image. On first compile it may take a few minutes while Docker fetch the ubuntu server 
and package installs specified in the Dockerfile. Subsequent compiles will be much faster as you Docker environment will have
cached these important first steps. Take a look at the Dockerfile in the project directory to see roughly how the server is constructed. 
Note: For following docker commands we assume you have Docker installed and your user is member of the docker group. 
Let's compile the docker server image,

```
 $ docker build -t myname/myimage:v1 ./
```

If build succeeds you can run the image locally using docker,

```
 $ docker run -it --rm --name myinstancename -p 80:80 -p 443:443 myname/myimage:v1
```
You can then visit the running website with you web browser, simply enter localhost into your browser.
To visit the admin interface enter https://localhost/admin into your browser. During development this
image ships with a self signed ssl security certificate, so you will have to accept a security exception
when visiting the admin interface locally.

The docker instance can be exited either by hitting Ctrl-D in the terminal where it was started, or if the instance is backgrounded
you should be able to stop or kill it using a Docker command, e.g.,

```
 $ docker kill myinstancename
```

DEVELOPMENT
---------------
The files that should be developed include all files in the project root directory and files under ./web2py/applications/.
The files in the root directory are mostly scripts and config files that help docker build a server image, and help configure
for example the Apache2 web server. The files under ./web2py/applications/ are the actual website development files and can be
developed and tested without compiling a docker image.

While developing the actual Docker image, it is often useful to start the image with a shell interface,
so that you can look around inside.  The environment is very much like an actual linux server, except 
there are no running processes / services by default.  To start the image with a shell interface run,

```
 $ docker run -it --rm --name myinstancename myname/myimage:v1 /bin/bash
```

Note that the default service (apache2) will not be started this way. If you check the running processes using $ top you will see
that the only visible processes are bash and top.

To work on developing the web2py website there is no need to constantly test it on a docker image. You can simply run web2py 
in development mode on you local machine by executing

```
 $ cd web2py
 $ python web2py.py
```

This will run your website in a development webserver that ships with web2py. The server allows you to test, develop and get immediate 
feedback when editing your website application files locally.  When you are ready you then create a Docker image as described above
to perform a full test of the web services or when you plan to deploy the image to a cloud service.

USEFUL DOCKER COMMANDS
------------------------
To list all downloaded / compiled docker images

```
 $ docker images
```

To list all docker instances

```
 $ docker ps -a
```

To remove a docker image

```
 $ docker rmi imagename   or   docker rmi imageid
```
To completely remove a docker instance (not just stop)

```
 $ docker rm instancename   or   docker rm instanceid
```
