# Time tracker

## Introduction
Time tracker is a small tool to keep track if your time. It deliberately keeps it simple and only supports a limited number of actions to keep track of. 

It is intended as a test case to learn React, therefore the source code may not be ideal.

Several important features are missing:
- configuration of the actions
- correction of registrations
- very limited reporting
- only support for sqlite
- security

Also, the docker image only runs gunicorn, which servers static assets as well. It would be better if static assets were served by a dedicated nginx instance.

## Development
The repository contains two separate sources:
- `app`, which contains the Python backend
- `jsx`, which contains the React frontend

For simplicity, the `static` directories in these sources are linked.

Both sources work independently from one another. It is thus important that the frontend knows the address of the backend. This can be configured in `jsx/Constants.js`.

### Python backend
A virtual environment can be created baed on `requirements.txt`. Git is configured to ignore the `venv` directory.

To run a development server, execute the following command in `python`.
```bash
FLASK_APP=app/timer.py FLASK_ENV=development FLASK_DEBUG=1 python -m flask run
``` 

### React frontend
An npm environment must be created in `jsx`. Git is configured to ignore the `jsx/node_modules` directory.

To run a development server, execute `npm run start` in `jsx`.

## Deployment
When deployed, there is no separate frontend server. Thus, the `HOST` in `jsx/Constants.js` must be set to an empty string.

To deploy, two steps are required:
- execute `npm run build` in `jsx`
- build the docker image from the Dockerfile 

Data is stored in the container in `/app/data`. If you want the data to be persisted, mount a volume to this location. 

As there is no configuration GUI yet, users and actions can be configured using a script such as `scripts/populate_db.py`.
