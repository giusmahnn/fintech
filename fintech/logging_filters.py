import logging


class UserContextFilter(logging.Filter):
    def filter(self, record):
        record.user_id = getattr(record, "user_id", "Anonymous")
        record.ip_address = getattr(record, "ip_address", "Unknown")
        return True