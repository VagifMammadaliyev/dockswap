 .. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/VagifMammadaliyev/dockswap/issues.

If you are reporting a bug, please try to use provided issue template. Also keep in mind that :code:`dockswap`
was initially written for my own needs. Some commands of :code:`dockswap` may not support the version
of :code:`docker` or :code:`docker-compose` you use. So please try to identify source of a problem and if you think
the problem is version incompatability then feel free to propose a **feature**.

Note: If the version of :code:`docker` or :code:`docker-compose` on your system matches the one specified in :code:`dockswap`
docs then issue a bug instead.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/VagifMammadaliyev/dockswap/issues.

If you are proposing a feature please make sure you describe it in details and keep in mind
that I am busy almost all of the time. You are free to implement it yourself or involve other contributors.

Bugs / Features
~~~~~~~~~~~~~~~

If you think you can help :code:`dockswap` work better like support more versions of dependent tools (:code:`docker` for example),
fix bugs or some new feature then you are free to contribute.


To set up a working environment:

1. Fork the :code:`dockswap` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/dockswap.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ python -m venv .venv
    $ cd dockswap/
    $ source .venv/bin/activate

4. Create a branch for local development::

    $ git checkout development  # make sure to create branches from development branch (not master)
    $ git checkout -b new/1-supporting-old-docker-compose  # for new features or...
    $ git checkout -b bug/2-windows-xp-crash               # for bug fixes or...
    $ get checkout -b fix/3-better-docs                    # for improvements of existing functionality

   Please make sure to use provided branch naming convention: :code:`{type}/{issue_number}-{short-description}`

5. By making changes you can test the script by running :code:`python -m dockswap.cli args... --options...`

6. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 dockswap tests
    $ python setup.py test or pytest
    $ tox

   To get dev dependecies run :code:`pip install -r requirements_dev.txt`

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m 'Provide a short description'
    $ git push origin new/1-supporting-old-docker-compose

   Or just :code:`git commit` (without :code:`-m` part) to provide more details about commit

8. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests if necessary.
2. If the pull request should update docs if necessary and may not update docs
   only in exceptional cases and if :code:`dockswap --help` is enough.
3. The pull request should work for Python 3.6, 3.7 and 3.8. Check
   https://travis-ci.com/VagifMammadaliyev/dockswap/pull_requests
   and make sure that the tests pass for all supported Python versions.

Deploying
---------

A reminder for the maintainers on how to deploy.
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags

Travis will then deploy to PyPI if tests pass.
