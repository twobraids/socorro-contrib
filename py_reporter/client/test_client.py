from random import choice
from py_reporter.client.py_client import CrashSubmitter
from configman.dotdict import DotDict

config = DotDict()
config.crash_submission_url = "http://127.0.0.1:8882/submit"

cs = CrashSubmitter(config, 'test_client', '0.0001')

some_exceptions = [
    Exception('the phase of the moon is incorrect'),
    Exception('your code hates you'),
    IOError("you can't write here"),
    OSError("it's not me, it's you"),
]



def alpha(x):
    for x in range(x):
        try:
            raise choice(some_exceptions)
        except Exception:
            cs.send_crash_report()

def beta(x=-1):
    if x == -1:
        return beta(random.randint(1, 5))
    if x <= 0:
        alpha(4)
    else:
        beta(x - 1)


def gamma(x=-1):
    if x == -1:
        raise choice(some_exceptions)
    if x <= 0:
        gamma()
    elif x % 2:
        gamma(x - 1)
    else:
        beta(x - 1)


alpha(4)
gamma(2)
beta(2)
gamma(3)
beta(0)
beta(5)

