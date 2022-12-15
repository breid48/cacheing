"""
Library containing various doubly linked list implementations intended to
be used with the cache's.
"""
from collections import OrderedDict


class _TTLLink:
    """Link in TTL Doubly Linked List.

    Attributes:
        key (hashable): Cache Item Key.
        expiry (int): Item Expiry Time.
        next (_TTLLink): Next Link in the DLL.
        prev (_TTLLink): Prev Link in the DLL. None
        if no previous link exists.
    """
    def __init__(self, key=None, expiry=None, nxt=None, prev=None):
        self.key = key
        self.expiry = expiry
        self.next = nxt
        self.prev = prev


class _TTLLinkedList:
    """Doubly Linked List of TTL Links.

    Attributes:
        head (_TTLLink): Head of the Linked List.
    """
    def __init__(self, head=None) -> None:
        self.__head = head
        # 'TTLCache' only inserts at the end of the
        # list. Reference to the tail of the list
        # for O(1) insertions.
        self.__tail = head

    @property
    def head(self):
        """Returns the head of the linked list."""
        return self.__head

    def insert(self, link):
        """Insert a new link at the end of the linked list.

        Args:
            link (_TTLLink): `_TTLLink` to insert.
        """
        if self.__head:
            link.prev = self.__tail
            link.prev.next = self.__tail = link
        else:
            self.__head = self.__tail = link

    def remove(self, link):
        """Remove a link from the linked list.

        Args:
            link (_TTLLink): `_TTLLink` to remove.
        """
        if self.__head == link:
            self.__head = self.__head.next
        elif self.__tail == link:
            self.__tail = self.__tail.prev
        else:
            link.prev.next = link.next
            link.next.prev = link.prev

    def sorted_insert(self, prev_link, link):
        """Sorted insert into the VTTL Linked List.

        Because VTTL cache items have variable
        time-to-lives, the VTTL Linked List is sorted
        in ascending order by expiry time.

        'prev_link' is determined by performing a binary
        search on the list represenation of the linked list.
        'prev_link' is the pivot link where link will be inserted.

        Args:
            prev_link (_TTLLink): pivot link where link will be inserted.
            link (_TTLLink): link to insert.
        """
        if not prev_link:
            self.__head = self.__tail = link
            return

        if prev_link.expiry <= link.expiry:
            link.next = prev_link.next
            link.prev = prev_link
            prev_link.next = link

            if self.__tail == prev_link:
                self.__tail = link

        else:
            link.next = prev_link
            link.prev = prev_link.prev
            prev_link.prev = link

            if self.__head == prev_link:
                self.__head = link


class LFUNode:
    """Object representing each item in the LFU cache.

    Each `LFUNode` contains its value and
    a pointer to its parent frequency node
    in the linked list.

    Args:
        key (hashable): Item Key.
        value (object): Item Value.
        parent (_LFUFreqNode): Parent `_LFUFreqNode.`
    """
    __slots__ = ['frequency', 'prev', 'next', 'items']

    def __init__(self, frequency, prev=None, next=None):
        self.frequency = frequency
        self.prev = prev
        self.next = next
        self.items = OrderedDict()


class LFULinkedList:
    """Doubly linked list of `LFUNode` objects. """

    __slots__ = ['head', 'node_cache']

    def __init__(self):
        self.head = LFUNode(frequency=0) # Dummy Head
        self.node_cache = {} # Mapping Keys -> LFULinkedList Nodes

    def insert(self, key):
        """Create and Insert a new item into the DLL.

        By default, all new elements are inserted with an access
        frequency of 1. If an item with the same key already exists
        in the linked list, we do not proceed with creation. Instead,
        it's value and access frequency is updated in an outer scope.

        Args:
            _key (hashable): Item Key.
            _value (object): Item Value.
        """
        head = self.head
        if not head.next:
            node = LFUNode(frequency=1, prev=head, next=None)
            head.next = node

        node = head.next
        node.items[key] = None
        self.node_cache[key] = node

    #@profile
    def increment(self, key):
        """Update the Access-Frequency of a Node.

        When an item in the cache is accessed, it's
        corresponding access frequency is incremented
        from N to N+1.
        If a frequency node with frequency N+1 exists,
        we move the _LFUNode to the new frequency list.
        If no frequency node exists with frequency N+1,
        we create the node, insert it into the linked list,
        and then move the node to this new frequency list.

        Args:
            node (_LFUNode): `_LFUNode` to access.
        """
        node = self.node_cache[key] # 14.4%
        del node.items[key] # 18.7%
        #node_next = node.next # 10.5%

        if node.next and node.next.frequency == node.frequency+1: # 11.8%
            node.next.items[key] = None # 16.5%
        else:
            new_node = LFUNode(frequency=node.frequency+1, prev=node, next=node.next)
            new_node.items[key] = None
            node.next = new_node

        self.node_cache[key] = node.next # 15.0%

    def delete(self, key):
        """Delete key from the linked list. """
        node = self.node_cache[key]
        del node.items[key]
        del self.node_cache[key]

    def popleft(self):
        """Evicts least-frequently used item from the cache.

        Removes all references to the least-frequently
        used `_LFUNode` from the `_LFUList` cache and linked lists.

        Returns:
            node.key (hashable): Item Key.
            node.value (object): Item Value.

        """
        curr = self.head.next
        while curr:
            if curr.items:
                key, _ = curr.items.popitem(False)
                del self.node_cache[key]
                return key
            curr = curr.next

        raise KeyError("cannot pop from empty cache.")
