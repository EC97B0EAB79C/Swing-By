import argparse
import logging

def setup_parser():
    parser = argparse.ArgumentParser(
        prog='Swing By',
        description='QNA with your knowledge base.'
        )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
        )
    

    return parser

def parse_args():
    # Set up argument parser
    parser = setup_parser()
    args = parser.parse_args()

    # Set logger
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    return args
    