from collections import OrderedDict

class _TTLLink:
    """Link in Linked List.

    """
    def __init__(self, key=None, expiry=None, nxt=None, prev=None):
        self.key = key
        self.expiry = expiry
        self.next = nxt
        self.prev = prev

    def get_key(self):
        return self.key


class _TTLLinkedList:
    """Linked List of TTL Links

    """
    def __init__(self, head=None) -> None:
        self.__head = head
        # Because we only insert at the end of the 
        # list. We can track the tail of the list 
        # for O(1) insertions.
        self.__tail = head

    @property
    def head(self):
        return self.__head

    def insert(self, link):
        """Insert a new link to the end of the linked list.

        Args:
            link (_TTLLink): `_TTLLink` to insert
        """
        if self.__head:
            link.prev = self.__tail
            self.__tail.next = self.__tail = link
        else:
            self.__head = self.__tail = link

    def remove(self, link):
        
        if self.__head == link:
            self.__head = link.next
        elif self.__tail == link:
            self.__tail = link.prev
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

        """
        if not prev_link:
            self.__head = self.__tail = link
            return

        if prev_link.expiry < link.expiry:
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

class _LFUNode:
    """Object representing each item in the cache.

    Each `LFUNode` contains its value and
    a pointer to its parent frequency node.

    Args:
        value (object):
        parent (_LFUFreqNode):

    """
    def __init__(self, key, value, parent):
        self.key = key
        self.value = value # Value of the Key: Value pair
        self.parent = parent # Pointer to parent `_LFUFreqNode`

class _LFUFreqNode:
    """Doubly linked list of `_LFUNode`
       objects sharing the same frequency.

    Args:
        frequency (int):
        nxt (_LFUFreqNode):
        prev (_LFUFreqNode):

    """
    def __init__(self, frequency, nxt, prev):
        self.frequency = frequency
        self.next = nxt
        self.prev = prev

        # Maintain an OrderedDict of `_LFUNode`
        # objects sharing the same frequency.
        # OrderedDict operations `move_to_end`
        # and _____ are O(1).
        self.items = OrderedDict()


class _LFUList:
    """Doubly Linked List of `_LFUFreqNode` objects

    Args:
        head (_LFUFreqNode): Head of the DLL

    """
    def __init__(self):
        self.head = _LFUFreqNode(0, None, None)
        self.cache = {} # Cache Mapping Keys to their respective
                        # `_LFUNode` objects.

    def print_list(self):
        """Debugging - Print List."""
        #        #
        #        #
        #        #
        #        #
        #        #
        #        #
        #        #
        #        #
        # REMOVE #
        hd = self.head
        
        while hd is not None:
            print(f"[Freq: {hd.frequency}]", end=" ")
            print("{", end="")
            for item in hd.items:
                print(f"{item.key}:{item.value}", end=" ")

            print("} -> ", end=" ")
            hd = hd.next
        print("\n\n\n")

    def delete_lfu_item(self):
        """Evicts least-frequently used item from the cache.

        Removes all references to the least-frequently 
        used `_LFUNode` from the cache and linked lists.

        Returns:
            node.key (hashable): Item Key
            node.value (object): Item Value

        """
        node = self.head.next.items.popitem(last=False)[0] # Pop & Retrieve LFU Item

        del self.cache[node.key]

        if not node.parent.items:
            self._remove_link(node.parent)

        return node.key, node.value

    def delete_node(self, node):
        """Remove _LFUNode from the Cache.

        Args:
            node (_LFUNode): `LFUNode` to remove.

        """
        del node.parent.items[node]

        if not node.parent.items:
            self._remove_link(node.parent)
   
        del self.cache[node.key]

    def _remove_link(self, node):
        """Remove frequency node from the doubly linked list.

        Args:
            node (_LFUFreqNode): `_LFUFreqNode` to remove.

        """
        if node.prev and node.next:
            node.prev.next = node.next
            node.next.prev = node.prev
        elif node.prev:
            node.prev.next = None
        elif node.next:
            node.next.prev = self.head
            self.head.next = node.next
        elif node == self.head:
            raise TypeError("can't remove head")

    def insert(self, _key, _value):
        """Create and Insert a new item into the
        DLL. By default, all new elements are
        inserted with a frequency of 1.

        Args:
            node (_LFUNode): `_LFUNode` to insert.

        """
        if self.cache.get(_key):
            return

        if not self.head.next or self.head.next.frequency > 1:
            parent = _LFUFreqNode(1, self.head.next, self.head)
            if self.head.next:
                self.head.next.prev = parent
            self.head.next = parent
        else:
            parent = self.head.next

        node = _LFUNode(_key, _value, parent)
        self.cache[_key] = node
        parent.items[node] = None

    def access_node(self, node):
        """Update the Access-Frequency of a Node.

        When a value in the cache is accessed, it's
        corresponding access frequency is incremented
        from N to N+1.
        If a frequency node with frequency N+1 exists,
        we move the node to the new frequency list.
        If no frequency node exists with frequency N+1,
        we create the node, insert it into the linked list,
        and then move the node to this new frequency list.

        Args:
            node (_LFUNode): `_LFUNode` to access.

        """
        freq = node.parent.frequency
        prev_parent = node.parent

        if node.parent.next:
            if node.parent.next.frequency == freq + 1:
                node.parent.next.items[node] = None
                node.parent = node.parent.next
            else:
                freq_node = _LFUFreqNode(freq + 1, nxt=node.parent.next, prev=node.parent)
                node.parent.next.prev = freq_node
                node.parent.next = freq_node
                node.parent = node.parent.next
                freq_node.items[node] = None
        else:
            freq_node = _LFUFreqNode(freq + 1, nxt=None, prev=node.parent)
            node.parent.next = freq_node
            node.parent = node.parent.next
            freq_node.items[node] = None

        del prev_parent.items[node]

        # After removal, if there's no _LFUNodes
        # sharing this frequency, delete the _FreqNode
        if not prev_parent.items:
            self._remove_link(prev_parent)