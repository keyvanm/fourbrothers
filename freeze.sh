#!/bin/bash

pip freeze > requirements.txt
sed -i.bak '/gnureadline/d' requirements.txt
sed -i.bak '/ipdb/d' requirements.txt
sed -i.bak '/ipython/d' requirements.txt
sed -i.bak '/Werkzeug/d' requirements.txt
