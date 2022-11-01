# pylint: skip-file

import unittest

from src.rcache.utils import _TTLLink, _TTLLinkedList


class TestLinkedList(unittest.TestCase):

    def setUp(self):
        self.default_linked_list = _TTLLinkedList()
        self.default_link = _TTLLink()

        self.pop_link = _TTLLink(key=1, expiry=60, nxt=None)
        self.pop_linked_list = _TTLLinkedList(head=self.pop_link)

    def test_linked_list_default_constructor(self):
        self.assertEqual(None, self.default_linked_list.head, msg='default linked list head is not none')

    def test_linked_list_constructor(self):
        self.assertEqual(self.pop_linked_list.head, self.pop_link)

    def test_linked_list_get_head(self):
        self.assertEqual(self.pop_linked_list.head, self.pop_link)
        self.assertEqual(self.default_linked_list.head, None)

    def test_linked_list_insert_empty_list(self):
        link = _TTLLink()
        self.default_linked_list.insert(link)

        self.assertEqual(self.default_linked_list.head, link, msg="insertion into empty list does not populate head of linked list")

    def test_linked_list_insert_link(self):
        link = _TTLLink()
        self.pop_linked_list.insert(link)

        self.assertEqual(self.pop_linked_list.head.next, link, msg="incorrect insertion into populated linked list")

    def test_linked_list_tail_node(self):
        link = _TTLLink()
        self.pop_linked_list.insert(link)

        self.assertEqual(None, self.pop_linked_list.head.next.next, msg="tail node in linked list does not point to None")


# .self.default_link <src.rcache._Link object at 0x7f65fac424c0>
# default head:  <src.rcache._Link object at 0x7f65fac42340> | default head next:  None
# pop head: <src.rcache._Link object at 0x7f65fac424f0> | pop head next: <src.rcache._Link object at 0x7f65fac42340>