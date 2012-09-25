Fuelstream Backend Stack
========================

This is a companion to `Thomas Reynolds'`_ article talking about the front-end stack for The `Nike Fuelstream`_ site.

Backend Stack
-------------
* `Amazon Elastic Load Balancer`_
* `Amazon CloudFront`_
* `Varnish Cache`_
* nginx_
* `Expression Engine`_

Overview
--------

The Fuelstream front-end gets its content from a JSON API powered by `Expression Engine`_. EE is a CMS built on PHP and CodeIgniter.
It provides a very powerful content-entry system with the ability to model data directly through the admin. This means that's
it's more than a CMS, it's an easy-to-provision PHP back-end system.

ExpressionEngine's performance isn't exceptional. It uses an EAV_, which provides plenty of flexibility, but requires lots of
SQL queries to generate content, especially
when the content is used to create a JSON API with hundreds of records rather than single pages, such as would be seen in a vanilla
CMS with "page" objects. EAVs also have trouble taking advantage of database joins, which are almost a necessity when building
complex queries that need to perform well.

Performance Improvements
------------------------

The first step to take when trying to improve performance is to simply reduce the number of requests to the server that the clients
make. This means offloading static asset requests for images and CSS to a CDN.  Amazon CloudFront makes this very easy. You just send
the client through CloudFront and it caches your content for you. Once it's on CloudFront, it never has to hit your servers again. CF
also has the very cool benefit of distributing your content around the world, so users get routing to a server that's close to them,
geographically.

Keeping *page* requests from hitting the server was a bit tougher. We use Amazon's Elastic Load Balancer to transparently proxy requests
to one of four web servers. On those web servers, we use `Varnish Cache`_ to store responses in memory. This means that once a page is requested,
regardless of the client that requested it, it's stored in RAM for a set amount of time. This makes subsequent requests extremely fast
since PHP is not invoked and data does not have to be retrieved from the database.

Varnish's normal mode of operation is similar to CloudFront's. On the first request for an uncached page, it will go to nginx (which
goes to PHP and retreives from the DB to render the page). Since our API responses take so long to generate (best case is still over four
seconds per request) we have to be very aggressive with our caching.  The solution here was to "warm" the cache automatically, making
sure that no client traffic ever hits uncached content.

Cache Warming
-------------
To warm the cache, we created a script that runs at an interval lower than the cache's timeout value. This script makes a special HTTP
request to the Varnish cache servers, telling them to do an in-place replacement of the cached content. It's an emotionless robot that
constantly surfs the site and makes sure the cache is minty fresh.

Conclusion
----------
This setup means that a normal request from a user viewing the FuelStream will *never* have to view uncached content.
Response times went from nearly ten seconds under load to 100ms with the cache enabled.

.. _Thomas Reynolds': http://awardwinningfjords.com/2012/09/23/fuelstream.html
.. _Nike Fuelstream: http://gameonworld.nike.com/#en_US/fuelstream
.. _Expression Engine: http://expressionengine.com/
.. _EAV: http://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model
.. _Varnish Cache: https://www.varnish-cache.org/
.. _nginx: http://nginx.org/
.. _Amazon CloudFront: http://aws.amazon.com/cloudfront/
.. _Amazon Elastic Load Balancer: http://aws.amazon.com/elasticloadbalancing/
