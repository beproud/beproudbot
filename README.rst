===================================
Haro
===================================

Haro is slackbot <https://github.com/lins05/slackbot> based beproud bot system.


事前準備
===================================

Requirements
-----------------

- Python 3.5.2 or later.

.. code-block:: bash

   $ python3 -m venv env
   $ git clone git@github.com:beproud/beproudbot.git
   $ cd beproudbot
   $ source /path/env/bin/activate
   (env)$ cp slackbot_settings.py.sample slackbot_settings.py
   (env)$ vi slackbot_settings.py
   (env)$ pip install -r beproudbot/requirements.txt


起動方法
==================

.. code-block:: bash

   $ source /path/env/bin/activate
   (env)$ python run.py
