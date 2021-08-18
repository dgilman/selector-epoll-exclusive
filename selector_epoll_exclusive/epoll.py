import selectors
import select


class EpollExclusiveSelector(selectors.EpollSelector):
    def register(self, fileobj, events, data=None):
        key = super(selectors._PollLikeSelector, self).register(fileobj, events, data)
        poller_events = select.EPOLLEXCLUSIVE
        if events & selectors.EVENT_READ:
            poller_events |= self._EVENT_READ
        if events & selectors.EVENT_WRITE:
            poller_events |= self._EVENT_WRITE
        try:
            self._selector.register(key.fd, poller_events)
        except:
            super().unregister(fileobj)
            raise
        return key
