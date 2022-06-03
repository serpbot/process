# process

## Installation

All the dependencies can be found in the requirements.txt file. This file contains both the specific packages as well as their exact versions required for proper functioning. It also makes it very easy to quickly setup as pip can read it directly.

> pip install -r requirements.txt

## Start process

The process can be launched in both dev and prod mode. The only different between these two modes is the configuration file that it reads from.

> python src/main.py --env dev

All the specific environment specific configuration is provided in the config folder (dev.ini and prod.ini). In these files, the following parameters are specified:

- SQS
- DB