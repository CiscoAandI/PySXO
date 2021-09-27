import functools

def cache(key):
    def decorator(f):
        @functools.wraps(f)
        def closure(self, *args, **kwargs):
            if getattr(self, key, None) and getattr(self, 'cache', None) is True:
                return getattr(self, key, None)
            setattr(self, key, f(self, *args, **kwargs))
            return getattr(self, key, None)
        return closure
    return decorator