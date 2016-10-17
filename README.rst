===================================
beproudbot
===================================

beproudbot

事前準備
===================================

virtualenvwapper にて環境を構築する。

.. code-block:: bash

   $ hg clone https://github.com/beproud/beproudbot
   $ cd beproudbot
   $ mkvirtualenv beproudbot
   $ pip install -r beproudbot/requirements.txt

起動
===================================

.. code-block:: bash

   $ cd beproudbot
   $ python run.py
