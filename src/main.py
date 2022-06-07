#!/usr/bin/env python3

import os
import sys
import logging.config
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/..")
from src.lib.search import get_rank, SearchEngineType
from src.lib.aws import receive_message, send_email
from src.lib.db import get_db_session, update_stats

log = logging.getLogger(__name__)


def run():
    log.info("Starting process")
    try:
        while True:
            message = receive_message()
            if message is not None:
                session = get_db_session()
                websites = json.loads(message["Body"])
                username = message["MessageAttributes"]["username"]["StringValue"]
                email = message["MessageAttributes"]["email"]["StringValue"]
                notifications = message["MessageAttributes"]["notifications"]["StringValue"]

                stats_websites = []
                for website in websites:
                    stats_keywords = []
                    domain = website["domain"]
                    for keyword in website["keywords"]:
                        # Get Bing rank
                        log.info("Looking up keyword (%s) for domain (%s) on Google" % (keyword["name"], domain))
                        bing_rank = get_rank(SearchEngineType.bing, keyword["name"], domain)
                        update_stats(session, keyword["id"], bing_rank, "bing")

                        # Get Google rank
                        log.info("Looking up keyword (%s) for domain (%s) on Bing" % (keyword["name"], domain))
                        google_rank = get_rank(SearchEngineType.google, keyword["name"], domain)
                        update_stats(session, keyword["id"], google_rank, "google")

                        stats_keywords.append({"keyword": keyword["name"], "bing_rank": bing_rank, "google_rank": google_rank})

                    stats_websites.append({"domain": domain, "keywords": stats_keywords})

                # Send email
                if notifications == "True":
                    send_email(email, username=username, websites=stats_websites)

                # Close DB conneciton
                session.close()

    except KeyboardInterrupt:
        log.info("Stopping service...")


if __name__ == "__main__":
    run()
