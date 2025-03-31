import attrs
from hikari.events.base_events import Event
from hikari.traits import RESTAware


@attrs.define()
class DebugMessageEvent(Event):
    app: RESTAware = attrs.field()

    content: str = attrs.field()
    """Message to send in the debug channel."""


@attrs.define()
class MainChannelMessageEvent(Event):
    app: RESTAware = attrs.field()

    content: str = attrs.field()
    """Message to send in the main info channel."""
