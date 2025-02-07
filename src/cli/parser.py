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
    logger = logging.getLogger()
    # Create file handler and set formatter
    file_handler = logging.FileHandler('swing-by.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    # Add handler to logger and set level
    logger.addHandler(file_handler)
    logger.setLevel(level)

    return args
    