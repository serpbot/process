import os
import logging
from jinja2 import Environment, FileSystemLoader

log = logging.getLogger(__name__)


def load_page(event_type, **kwargs):
    """Render html page using jinja"""
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
        with open(basedir + "/../templates/" + event_type + ".html") as file:
            template = Environment(loader=FileSystemLoader("./templates")).from_string(file.read())
            return template.render(**kwargs)
    except Exception as exception:
        log.error("Unable to load template (%s): %s", event_type, exception)
