from rest_framework.throttling import BaseThrottle
from django.conf import settings
from django.core.cache import cache
import time
import logging

logger = logging.getLogger("throttling")

class CustomRateThrottle(BaseThrottle):
    def __init__(self):
        self.rate = None
        self.num_requests = None
        self.duration = None
        self.history = None

    def allow_request(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser:
                self.rate = settings.RATE_LIMITS["superuser"]
            elif user.roles.filter(name="Admin").exists():
                self.rate = settings.RATE_LIMITS["admin"]
            elif user.roles.filter(name="Support").exists():
                self.rate = settings.RATE_LIMITS["support"]
            else:
                self.rate = settings.RATE_LIMITS["regular_user"]
        else:
            self.rate = settings.RATE_LIMITS["anonymous"]
        
        self.num_requests, self.duration = self.parse_rate(self.rate)
        self.history = cache.get(self.cache_key(request), [])

        now = time.time()
        self.history = [timestamp for timestamp in self.history if timestamp > now - self.duration]

        if len(self.history) >= self.num_requests:
            logger.warning(f"Rate limit exceeded for user: {request.user} (IP: {self.get_ident(request)})")
            return False
        
        self.history.append(now)
        cache.set(self.cache_key(request), self.history, self.duration)
        return True
    
    def parse_rate(self, rate):
        if rate is None:
            return None, None
        num, period = rate.split("/")
        num_requests = int(num)
        if period == "second":
            duration = 1
        elif period == "minutes":
            duration = 60
        elif period == "hours":
            duration = 60 * 60
        elif period == "days":
            duration = 60 * 60 * 24
        else:
            raise ValueError(f"Invalid rate period: {period}")
        return num_requests, duration

    def cache_key(self, request):
        if request.user.is_authenticated:
            return f"Throttle_{request.user.id}"
        return f"throttle_{self.get_ident(request)}"
    
    def wait(self):
        """
        Returns the time (in seconds) until the next request is allowed.
        """
        if self.history:
            now = time.time()
            remaining_time = self.duration - (now - self.history[0])
            return max(remaining_time, 0)
        return None