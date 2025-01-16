import logging

WARNING = "\033[33mWARNING\033[0m: "
logger = logging.getLogger(__name__)

class WarningProcessor:
    @staticmethod
    def process_warning(message, abort = False, script_mode = False):
        if script_mode:
            return False
        user_continue = input(message) == 'y'
        if abort and not user_continue:
            logger.fatal("\033[31mABORTED\033[0m")
            exit(1)
        return user_continue

    @classmethod
    def process_article_warning(self, abort, service, request, fetched):
        message = WARNING + f"""Fetched paper might be not correct ({service})
\tRequested:\t{request}
\tFetched:\t{fetched}
\tDo you want to use fetched paper? (y/N): """
        return self.process_warning(message, abort)