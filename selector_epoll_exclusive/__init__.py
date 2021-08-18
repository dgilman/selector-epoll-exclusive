import select


if hasattr(select, "epoll") and hasattr(select, "EPOLLEXCLUSIVE"):
    from .epoll import EpollExclusiveSelector
