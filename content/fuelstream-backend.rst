Nike+ FuelStream Backend Stack
==============================

This is a companion to `Thomas Reynolds'`_ article outlining the front-end stack for The `Nike+ FuelStream`_ site.

Backend Stack
-------------
* `Amazon Elastic Load Balancer`_ (ELB)
* `Amazon CloudFront`_ (CF)
* `Varnish Cache`_
* nginx_
* `Expression Engine`_
* `PHP`_ (FPM, with APC enabled)
* `GlusterFS`_
* `Amazon RDS`_

Overview
--------
The FuelStream front-end gets its content from a JSON API powered by `Expression Engine`_. EE is a CMS built on PHP and CodeIgniter.
It provides a very powerful content-entry system with the ability to model data directly through the admin. This means that's
it's more than a CMS, it's an easy-to-provision PHP back-end system.

ExpressionEngine's performance is not exceptional. It uses an EAV_, which provides plenty of flexibility, but requires lots of
SQL queries to generate content, especially when the content is used to create a JSON API with hundreds of records rather than 
single pages, such as would be seen in a vanilla CMS with "page" objects. EAVs also have trouble taking advantage of database 
joins, which are almost a necessity when building complex queries that need to perform well. We were faced with a serious
problem since our API requests were taking close to **20 seconds** to complete when the site was under load.

We used `Amazon RDS`_ for the database. Nothing special there, you pay a little more to have Amazon manage the database OS, optimization, 
replication, and you get some nice tools to do point-in-time restoration. If you're using MySQL and EC2, it's a no-brainer.

All components of the cluster have full redundancy:

- 4 web/application servers (Varnish, nginx, PHP)
- 2 file servers (GlusterFS)
- The built-in redundancy and health-checking of Cloudfront, ELB, and RDS

Distributing Assets
-------------------
A common issue when your webapp outgrows a single server setup is how to distribute assets among the servers. There are several
ways to solve this including directing all content-generating traffic to a single server and replicating the assets via rsync. I've
found that using `GlusterFS`_ provides a very robust and reliable system for file replication.

GlusterFS is very cool.  Two servers in the cluster do nothing but store files. The web-servers have a network filesystem share and file writes
to that share are immediately replicated to both GlusterFS servers. Every asset stored in Gluster essentially has two physical copies, one
on each file server. If one of them goes down, the GlusterFS client (on the web-servers) is smart enough to switch to the other
server. When the server comes back up, it heals itself from the active server. 

Of course, all of this redundancy and reliability comes with a huge cost. File access performance is greatly reduced. There are some efforts to 
improve the client-side caching that Gluster does, but I've found that it's still lacking. 

Performance Improvements
------------------------
The easiest way to improve performance of a web app is to simply reduce the number of requests to the server that the clients
make. This means offloading static asset requests for images and CSS to a CDN.  `Amazon CloudFront`_ makes this very easy. You just send
the client through CloudFront and it caches your content for you. Once it's on CloudFront, it never has to hit your servers again. CF
also has the very cool benefit of distributing your content around the world, so users get routed to a server that's close to them
geographically.

Keeping *page* requests from hitting the server was a bit tougher. We use Amazon's Elastic Load Balancer to transparently proxy requests
to one of four web servers. On those web servers, `Varnish Cache`_ sits in front of nginx and works as a caching proxy. Once a page is requested
and rendered, it's stored in RAM for a set amount of time, regardless of who made the initial request. This makes subsequent requests extremely fast
since PHP is not invoked and data does not have to be retrieved from the database, it can be served directly from RAM.

:: 

    uncached request: client -> ELB -> Varnish -> nginx -> PHP -> database
      cached request: client -> ELB -> Varnish (RAM cache)

Since our API responses take so long to generate we have to be very aggressive with our caching.  The solution here was to "warm" the 
cache automatically, making sure that no client traffic ever hits uncached content.

Note that FuelStream has a huge benefit over most web apps since it's session-less. There is no use of user-login or history.
Whenever you introduce sessions to an application, caching becomes much more difficult.

Cache Warming
-------------
To warm the cache, we created a script that runs at an interval lower than the cache's timeout value. This script makes a special HTTP
request to the Varnish cache servers, telling them to do an in-place replacement of the cached content from the database. (using the ``req.hash_always_miss`` 
variable in Varnish VCL) Only the warming script gets to see the slow loading times. It's an emotionless robot that constantly 
surfs the site and makes sure the cache is minty fresh.

Conclusion
----------
This setup means that a normal API request from a user viewing the FuelStream will *never* hit uncached content and be forced to wait.
Response times went from a dismal 10-20 seconds under load to 100ms or less with the cache enabled.

.. _Thomas Reynolds': http://awardwinningfjords.com/2012/09/23/fuelstream.html
.. _Nike+ FuelStream: http://gameonworld.nike.com/#en_US/fuelstream
.. _Expression Engine: http://expressionengine.com/
.. _EAV: http://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model
.. _Varnish Cache: https://www.varnish-cache.org/
.. _nginx: http://nginx.org/
.. _GlusterFS: http://www.gluster.org/
.. _Amazon CloudFront: http://aws.amazon.com/cloudfront/
.. _Amazon Elastic Load Balancer: http://aws.amazon.com/elasticloadbalancing/
.. _Amazon RDS: http://aws.amazon.com/rds/
.. _PHP: http://www.php.net/
