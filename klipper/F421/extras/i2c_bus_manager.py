BUS_OWNER = None


def acquire(owner):
    global BUS_OWNER

    if BUS_OWNER is not None and BUS_OWNER != owner:
        return False

    BUS_OWNER = owner
    return True


def release(owner):
    global BUS_OWNER

    if BUS_OWNER == owner:
        BUS_OWNER = None


def is_busy():
    return BUS_OWNER is not None


def is_busy_by_other(owner):
    return BUS_OWNER is not None and BUS_OWNER != owner


def get_owner():
    return BUS_OWNER