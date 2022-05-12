#! usr/bin/bash

source .venv/bin/activate
export LIBRARY_PROJECT_PATH=`pwd`
cd front_end
npm run build
cd ..
python ./manage.py makemigrations
python ./manage.py migrate
python ./manage.py collectstatic
