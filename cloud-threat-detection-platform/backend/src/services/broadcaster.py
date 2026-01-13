# backend/src/services/broadcaster.py
import asyncio
import uuid
from typing import Dict

class Broadcaster:
    """
    Very small pub/sub broadcaster. Each subscriber gets an asyncio.Queue.
    The publisher pushes events to all queues.
    """
    def __init__(self):
        # map subscriber_id -> asyncio.Queue
        self.subscribers: Dict[str, asyncio.Queue] = {}
        self.lock = asyncio.Lock()

    async def subscribe(self) -> (str, asyncio.Queue):
        """Create a queue for a new subscriber and return (id, queue)."""
        q = asyncio.Queue()
        sid = str(uuid.uuid4())
        async with self.lock:
            self.subscribers[sid] = q
        return sid, q

    async def unsubscribe(self, sid: str):
        async with self.lock:
            q = self.subscribers.pop(sid, None)
            if q is not None:
                # drain queue to avoid pending put waits
                while not q.empty():
                    try:
                        q.get_nowait()
                        q.task_done()
                    except asyncio.QueueEmpty:
                        break

    async def publish(self, event: dict):
        """Push event to all subscribers (non-blocking)."""
        async with self.lock:
            subs = list(self.subscribers.items())
        for sid, q in subs:
            # put_nowait so one slow consumer won't block publisher
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                # if queue full, drop the event for that subscriber
                # (or consider using a larger queue)
                pass

# Single global broadcaster instance that other modules can import
broadcaster = Broadcaster()
