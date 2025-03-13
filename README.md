# Autism DRIVE deployment repository

## Deploying a release

### Set up your local Development Environment
1. Clone both of these repositories in the same directory:
   - [`autismdrive/autismdrive`](https://github.com/autismdrive/autismdrive)
   - [`autismdrive/autismdrive-dist`](https://github.com/autismdrive/autismdrive-dist)
2. Your directory structure should look like this:
    ```
    ./
    ├── autismdrive/
    └── autismdrive-dist/
        ├── README.md (this file)
        ├── prepare_for_deploy.sh
        ├── backend/
        ├── frontend/
        └── ...
   ```
3. Follow the instructions in the README files in the `frontend` and `backend` directories in the `autismdrive` repository to set up your local development environment.

### Create a release tag in the `autismdrive` repository
1. Make sure you have committed (or merged via PR) all your changes to the `main` branch of the `autismdrive` repository.
2. In GitHub, navigate to the [Releases](https://github.com/autismdrive/autismdrive/releases) page for the [`autismdrive`](https://github.com/autismdrive/autismdrive) repository.
3. Click on the "Draft a New Release" button.
4. Click "Choose a tag" and increment the most recent version number, following [semantic versioning](https://semver.org/) rules.
5. Select `main` as the Target branch.
6. Fill in the Release title and description with the relevant information.
7. Click the "Publish release" button.
8. This will create a new release tag in the `autismdrive` repository.

### Generate a new Production build
1. Set up your local development environment according to the "Local dev environment setup" instructions above.
2. Generate a release tag in the `autismdrive` repository.
3. Open a command line terminal and navigate to this directory (`autismdrive-dist`).
4. Run the `./prepare_for_deploy.sh` script found in the same directory as this README file.
5. This will replace the `frontend` and `backend` directories in this directory and stage the changes for commit.
6. Commit the changes and push to the `main` branch of this repository (`autismdrive-dist`).

## Create a release tag in the `autismdrive-dist` repository
1. Make sure you have committed (or merged via PR) all your changes to the `main` branch of the `autismdrive-dist` repository.
2. In GitHub, navigate to the [Releases](https://github.com/autismdrive/autismdrive-dist/releases) page for the [`autismdrive-dist`](https://github.com/autismdrive/autismdrive-dist) repository.
3. Click on the "Draft a New Release" button.
4. Click "Choose a tag" and enter the same release number you used above.
5. Select `main` as the Target branch.
6. Fill in the Release title and description with the same information as above.
7. Click the "Publish release" button.
8. This will create a new release tag in the `autismdrive-dist` repository.

## Deploy to the public & private servers
1. Log in to the UVA High Security VPN.
2. SSH to the public and private servers (see [the `admin` repo](https://github.com/autismdrive/admin) for details).
3. Switch to superuser with `sudo su` and enter your password.
4. Navigate to the `/var/www/autismdrive-dist` directory.
5. Checkout the branch for the release tag you created above:
    ```bash
    git fetch --tags
    git checkout tags/<tag_name>
    ```
6. Activate the Python virtual environment, set the Flask app environment variable, and rebuild the index:
    ```bash
    export APP_DIR=`pwd`
    source ${APP_DIR}/backend/python-env/bin/activate
    export FLASK_APP=${APP_DIR}/backend/app/__init__.py
    cd ${APP_DIR}/backend
    pip install -r requirements.txt
    flask db upgrade
    flask clearindex
    flask initindex
    ```
7. Reload Apache to apply the changes:
    ```bash
    systemctl reload apache2.service
    ```
