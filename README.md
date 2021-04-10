# FPL Assistant
The API for the FPL Assistant
## Local Setup
Perform the following steps:
1. Install requirements in either a virtualenv or your system
   ```sh
   $ pip install -r requirements.txt
   ```
2. Source the <kbd>setup.sh</kbd> file
   ```sh
   $ source setup.sh <path-to-volume-mount>
   ```
   where, <kbd>path-to-volume-mount</kbd> refers to the absolute path to the DB volume
3. Initialize database
   ```sh
   $ flask initdb
   ```
   Need to run on the first run but not necessary every time
4. Run API
   ```sh
   $ flask run
   ```
Now the API should be accessible at port 5000 on <kbd>localhost</kbd>
