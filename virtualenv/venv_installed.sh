#!/usr/bin/env bash

if [[ $(python3 -m pip freeze) != *virtualenv* ]]; then
		echo -e "--> Virtualenv not installed. Installing..."
		python3 -m pip install virtualenv
fi

echo -e "--> Virtualenv installed sucessfully. Creating environment..."
virtualenv -p $(which python3) ../venv

echo -e "--> Environment created. Enter with \`source venv/bin/activate\`"

exit 0
