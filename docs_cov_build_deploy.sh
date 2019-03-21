#!/bin/sh

# coverage: clean, build, deploy
rm -rf htmlcov
sudo rm -rf /var/www/PyOTRS/htmlcov
/usr/local/bin/coverage html -d htmlcov
sudo cp -a htmlcov /var/www/PyOTRS/

# docs: clean, build, deploy
rm -rf build/docs
sudo rm -rf /var/www/PyOTRS/docs
tox -e docs
sudo cp -a build/docs /var/www/PyOTRS/docs

# check format (README)
python setup.py check --strict --metadata --restructuredtext
