

class ListNode:
    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None  # Front
        self.tail = None  # Back
        self.size = 0     # Tracks size in O(1)

    def push_front(self, value):
        new_ListNode = ListNode(value)
        new_ListNode.next = self.head
        if self.head:
            self.head.prev = new_ListNode
        else:
            self.tail = new_ListNode  # Empty list
        self.head = new_ListNode
        self.size += 1

    def push_back(self, value):
        new_ListNode = ListNode(value)
        new_ListNode.prev = self.tail
        if self.tail:
            self.tail.next = new_ListNode
        else:
            self.head = new_ListNode  # Empty list
        self.tail = new_ListNode
        self.size += 1

    def pop_front(self):
        if not self.head:
            raise IndexError("pop from empty list")
        value = self.head.value
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None  # List is now empty
        self.size -= 1
        return value

    def pop_back(self):
        if not self.tail:
            raise IndexError("pop from empty list")
        value = self.tail.value
        self.tail = self.tail.prev
        if self.tail:
            self.tail.next = None
        else:
            self.head = None  # List is now empty
        self.size -= 1
        return value

    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __iter__(self):
        current = self.head
        while current:
            yield current.value
            current = current.next

    def __repr__(self):
        return "LinkedList([" + ", ".join(str(v) for v in self) + "])"

