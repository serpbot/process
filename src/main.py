#!/usr/bin/env python3

import os
import sys
import logging.config
import argparse
import configparser
import json

from src.lib.search import get_rank, search, SearchEngineType
from src.lib.aws import receive_message, send_email
from src.lib.db import get_db_session, update_stats

log = logging.getLogger(__name__)


def get_conf(env):
    """Get config object"""
    config = configparser.ConfigParser()
    basedir = os.path.abspath(os.path.dirname(__file__))
    if env == "prod":
        config.read(basedir + "/conf/prod.ini")
    else:
        config.read(basedir + "/conf/dev.ini")
    return config


def get_env():
    """Get environment to run in"""
    parser = argparse.ArgumentParser(description="Serpbot backend.")
    parser.add_argument("-e", "--env", default="dev",
                        help="select an environment to launch in (dev, prod)")
    args = parser.parse_args()
    if args.env.lower() not in ["dev", "prod"]:
        log.error("Invalid environment selected")
        sys.exit(1)
    return args.env.lower()


def run(env):
    log.info("Starting in %s mode", env)
    conf = get_conf(env)
    try:
        while True:
            message = receive_message(conf["sqs"]["name"], conf["sqs"]["region"])
            if message is not None:
                session = get_db_session(conf)
                websites = json.loads(message["Body"])
                username = message["MessageAttributes"]["username"]["StringValue"]
                email = message["MessageAttributes"]["email"]["StringValue"]

                for website in websites:
                    domain = website["domain"]
                    for keyword in website["keywords"]:
                        # Get Bing rank
                        log.info("Looking up keyword (%s) for domain (%s) on Google" % (keyword["name"], domain))
                        bing_rank = get_rank(SearchEngineType.bing, keyword["name"], domain)
                        update_stats(session, keyword["id"], bing_rank, "bing")

                        # Get Google rank
                        log.info("Looking up keyword (%s) for domain (%s) on Bing" % (keyword["name"], domain))
                        google_rank = get_rank(SearchEngineType.bing, keyword["name"], domain)
                        update_stats(session, keyword["id"], google_rank, "google")

                # Send email
                # send_email(email, domain=domain.domain)

                # Close DB conneciton
                session.close()

    except KeyboardInterrupt:
        log.info("Stopping service...")


if __name__ == "__main__":
    run(get_env())
