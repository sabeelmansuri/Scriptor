<img src="https://i.imgur.com/DVGP07n.png" alt="Scriptor" width=300px>

## Introduction
Scriptor is a solution for streamlining studying and reviewing at the University of California, San Diego. No longer do students have to manually search for specific information in the vast collection of knowledge that is the UC San Diego Podcast System. 

Scriptor allows students to search for keywords and instantly be presented with the exact material they want. Scriptor returns precise timestamps in podcasts that match the information users seek, efficiently parsing through UCSD's vast database so students don't have to. Scriptor wraps this functionality with a personalized interface, allowing users to favorite, save their history, and more. Happy podcasting!
 
## Requirements
- [ ] **Operating System:** Desktop/Laptop | Mac/Linux
- [ ] **Browser:** Google Chrome, latest release
- [ ] **Software:** Docker, Node, NPM, Git


## Installation Instructions
If you want to install and build Scriptor locally, enter the following commands:
```shell
git clone https://github.com/nlpathak/Scriptor
cd Scriptor
docker-compose build --no-cache
```

## How to Run
#### Starting
If you want to run Scriptor locally, enter the following commands:
```shell
docker-compose up -d frontend

# Run the below line once http://localhost:5000 returns "{success:true}". You only have to run the below import script when installing this project for the first time, or after clearing the database data with: docker-compose down -v.

docker-compose exec backend python3 scripts/import_data_into_elasticsearch.py
```

The app will be accessible at [http://localhost:3000](http://localhost:3000). The backend API will be accessible at [http://localhost:5000](http://localhost:5000).

#### Stopping
To stop running the application (but retain the database), enter the following:
```shell
docker-compose down
```

## In Case of Failure
If you get an error about possible orphan containers, run:
``` shell
docker-compose down --remove-orphans
```

End the application and clear all data with:
```shell
docker-compose down -v
```

Then, restart the application with:
```shell
docker-compose up -d frontend

# And since all data has been cleared, re-run the data import script (after waiting for about 20-30 secs)
# Wait until localhost:5000 returns {success:true}

docker-compose exec backend python3 scripts/import_data_into_elasticsearch.py
```

## To Start Fresh
Optionally, pull the latest code from Github.
``` shell
docker-compose down -v --remove-orphans
docker-compose build --no-cache
docker-compose up -d frontend

# Wait until localhost:5000 returns {success:true}
docker-compose exec backend python3 scripts/import_data_into_elasticsearch.py
```

## Deleting All Stored Users
``` shell
# Wait until localhost:5000 returns {success:true}
docker-compose exec backend python3 scripts/clear_users.py
```

## Notes
* All commands in the Installation, How to Run, and In Case of Failure sections should be run in the top-level, `Scriptor/` directory.
* At this time, only the following classes are available for searching due to expensive computations: 
  * `CHEM 4 [FA18]` `CSE 190 [FA18]` `CSE 101 [WI19]` `CSE 20 [FA18]` `CSE 20 [SP19]` `CSE 141 [FA18]` `COGS 9 [WI19]` `MATH 18 [WI18]` `CSE 21 [SP19]` `BIBC 120 [SP19]` `MATH 183 [FA19]` `MATH 183 [SP19]`
* Results for the same query will be ordered differently from search-to-search because the search implementation is not programmed to break ties for equivalent relevance scores consistently.

## Known Bugs
* The `docker` commands sometimes return errors. This can be fixed by prepending every command with `sudo`.
* The Forgot Password verification email is almost always sent to the user's spam folder.
* Due to security limitations for the needed files for Forgot Password, this functionality is not available for extensions of this project (i.e. your copy).
