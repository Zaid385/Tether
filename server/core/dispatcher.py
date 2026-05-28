from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from server.core.controller import ServerController

class PacketDispatcher:
    """Dispatches packets to the appropriate handlers based on type."""
    def __init__(self, controller: 'ServerController'):
        self.controller = controller
        self.handlers = {}

    def register_handler(self, packet_type: str, handler_func):
        self.handlers[packet_type] = handler_func

    def dispatch(self, client_handler, packet):
        handler = self.handlers.get(packet.type)
        if handler:
            handler(client_handler, packet)
        else:
            self.controller.logger.warning(f"No handler registered for type: {packet.type}")
