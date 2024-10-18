#!/usr/bin/env bash

###################################################################################################
# WARNING: Run this script from your local development environment, not on the Production server!
#
# Deletes the current frontend and backend directories and replaces them with the latest
# built versions of the frontend and backend. This script is intended to be run from the
# autismdrive-dist directory.
#
# Assumes this script is in a directory called `autismdrive-dist`
# and that the directory ../autismdrive exists and contains the
# autismdrive/autismdrive repository, like so:
#    ./
#    ├── autismdrive/
#    └── autismdrive-dist/
#        ├── prepare_for_deploy.sh
#        ├── backend/
#        ├── frontend/
#        └── ...
#
# After running this script, commit the changes to the `autismdrive-dist` git repository.
# See the README file in this repository for further deployment instructions.
###################################################################################################

# Clear out old directories
rm -rf backend/
rm -rf frontend/

# Build the frontend and backend from the source code
cd ../autismdrive/frontend
ng build --prod -c production
cd ../../autismdrive-dist/

# Copy the built frontend and backend into the autismdrive-dist directory
cp -r ../autismdrive/frontend/dist/autismdrive/ frontend/
cp -r ../autismdrive/backend backend

# Remove unnecessary files and directories
rm -rf backend/python-env
rm -rf backend/.idea
rm -rf backend/instance
rm -rf backend/tests
rm -rf star_drive.log
rm -rf __pycache__/

# Add the new frontend and backend to the git staging area
git add backend
git add frontend
