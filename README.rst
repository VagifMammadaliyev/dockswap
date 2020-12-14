========
DockSwap
========


.. image:: https://img.shields.io/pypi/v/dockswap.svg
        :target: https://pypi.python.org/pypi/dockswap

.. image:: https://img.shields.io/travis/VagifMammadaliyev/dockswap.svg
        :target: https://travis-ci.com/VagifMammadaliyev/dockswap

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black



Tool for easier switching between projects that uses docker containers to set up working environment


Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install dockswap

Usage
~~~~~

.. code-block:: bash

   Usage: dockswap [OPTIONS] COMMAND [ARGS]...

   DockSwap. Tool for swapping projects.

   Commands:
     add      Register a composer for project
     delete   Delete registered composer
     list     List all registered composers
     prune    Prune existing registered composers.
     start    Start containers for registered composer
     stop     Stop containers for registered composer
     stopall  Stop (and/or remove) all running containers
     version  Show version of currently used dockswap


Adding composer
---------------

.. code-block:: bash

   Usage: dockswap add [OPTIONS] PROJECT_NAME

     Register a composer for project

   Arguments:
     PROJECT_NAME  [required]

   Options:
     --path PATH      Path to .yml or .json file that must be run using docker-
                      compose  [required]

     --env-path PATH  If your docker-compose file uses env_file then specify path
                      for that file


Showing composers
-----------------

.. code-block:: bash

   Usage: dockswap list [OPTIONS]

     List all registered composers

   Options:
     --full / --no-full  show more info  [default: False]


Starting
---------------

.. code-block:: bash

   Usage: dockswap start [OPTIONS] PROJECT_NAME

     Start containers for registered composer

   Arguments:
     PROJECT_NAME  [required]

   Options:
     --remove-other / --no-remove-other
                                     Remove stopped containers  [default: False]
     --dry / --no-dry                Do not run command, instead just print it
                                     [default: False]


Why?
----

If your are using docker containers to set up your working environment then this tool is for you.
I used to do like this::

    $ cd ~/projects/foo
    $ docker stop $(docker ps -aq) && docker rm $(docker ps -aq)
    $ docker-compose -f _dev/docker-compose.yml up -d

Then I want to switch to another project, and again::

    $ cd ~/projects/bar
    $ docker stop $(docker ps -aq) && docker rm $(docker ps -aq)
    $ docker-compose -f _directory_with_another_name/docker-compose.yml up -d


This is a bit verbose for such a simple task. Now what I do is just::

    $ dockswap start foo --remove-other
