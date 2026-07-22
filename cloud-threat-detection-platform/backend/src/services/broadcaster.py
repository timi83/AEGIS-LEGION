# backend/src/services/broadcaster.py
import asyncio
import uuid
from typing import Dict, Optional, Tuple

class Broadcaster:
    """
    Small pub/sub broadcaster, partitioned by organization for tenant isolation.
    Each subscriber registers with its organization id; an event is delivered
    only to subscribers of the same organization.
    """
    def __init__(self):
        # subscriber_id -> (organization_id, queue)
        self.subscribers: Dict[str, Tuple[Optional[int], asyncio.Queue]] = {}
        self.lock = asyncio.Lock()

    async def subscribe(self, organization_id: Optional[int]) -> Tuple[str, asyncio.Queue]:
        """Create a queue for a new subscriber scoped to its organization."""
        q = asyncio.Queue()
        sid = str(uuid.uuid4())
        async with self.lock:
            self.subscribers[sid] = (organization_id, q)
        return sid, q

    async def unsubscribe(self, sid: str):
        async with self.lock:
            entry = self.subscribers.pop(sid, None)
        if entry is not None:
            _, q = entry
            # drain queue to avoid pending put waits
            while not q.empty():
                try:
                    q.get_nowait()
                    q.task_done()
                except asyncio.QueueEmpty:
                    break

    async def publish(self, event: dict, organization_id: Optional[int] = None):
        """
        Push an event to subscribers of the given organization only.

        Tenant safety: if organization_id is None the event is NOT broadcast to
        anyone (rather than to everyone) — a missing org id must never leak an
        event across tenants. Callers should always pass the event's org id.
        """
        if organization_id is None:
            return
        async with self.lock:
            subs = list(self.subscribers.items())
        for sid, (sub_org, q) in subs:
            if sub_org != organization_id:
                continue
            # put_nowait so one slow consumer won't block the publisher
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                # drop the event for that subscriber if its queue is full
                pass

# Single global broadcaster instance that other modules can import
broadcaster = Broadcaster()
