class _Link:
    """Link in Linked List.

    """
    def __init__(self, key=None, expiry=None, next=None):
        self.key = key
        self.expiry = expiry
        self.next = next

    def get_key(self):
        return self.key


class _LinkedList:
    """Linked List of TTL Links

    """
    def __init__(self, head=None) -> None:
        self.head = head

    def get_head(self):
        return self.head

    def insert_link(self, link):
        if not isinstance(link, _Link):
            raise TypeError(f"cannot insert type {type(link)} \
                            into linked list")

        if self.head:
            head = self.head
            while head.next:
                head = head.next
            head.next = link
        else:
            self.head = link

    def remove_link(self, link):

        if self.head.key == link.key:
            self.head = self.head.next
            return True

        head = self.head
        last = head
        while head:
            if head.key == link.key:
                last.next = head.next
                return True
            last = head
            head = head.next

        raise KeyError("invalid link")
