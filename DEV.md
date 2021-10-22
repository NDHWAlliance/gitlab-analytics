# Development Document

## setup development environment

### Run & Debug in command line

1. clone repo
2. create python virtualenv

        virtualenv --python3 env

3. install requirements

        source env/bin/activate
        pip install -r server/requirements.txt
        pip install -r server/requirements-dev.txt

4. start

        cd server
        export FLASK_APP=ga
        python -m flask run

### Run & Debug in IDE

1. clone repo
2. open project in PyCharm
3. create python interpreter in PyCharm preference.

   1. Preference - Project: gitlab-analytics - Python Interpreter - Add
   2. virtualenv

4. install requirements

   1. `pip install -r server/requirements.txt`
   2. `pip install -r server/requirements-dev.txt`

5. Preference - Project: gitlab-analytics - Python Project Structure
   1. set "server" as Sources

6. Add Configuration
   1. Add Configuration 
   2. flask server 
   3. Target type: Module name 
   4. Target: `ga` 
   5. Working directory: `$path/to/repo/server`
