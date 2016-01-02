from logger import logger

events = {}

def subscribe(event):
    if event not in events:
        events[event] = set()
    def f(body):
        events[event].add(body)
        return body
    return f

def notify(event, *args, **kargs):
    if event in events:
        for b in events[event]:
            try:
                b(*args, **kargs)
            except Exception as e:
                logger.warning(e)

def remove(event, body):
    if event in events:
        if body in events[event]:
            events[event].remove(body)
