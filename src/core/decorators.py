import functools

def cache(key):
    def decorator(f):
        @functools.wraps(f)
        def closure(self, *args, **kwargs):
            if getattr(self, key, None):
                return getattr(self, key, None)
            setattr(self, key, f(self, *args, **kwargs))
            return getattr(self, key, None)
        return closure
    return decorator