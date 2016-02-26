## 0.40 (2016-02-xx)

- Add method `Communicator.get_packet(block=True, timeout=1)`.
  Fetching packets via `Communicator.receive.get()` is now deprecated, and will change to [PriorityQueue](https://docs.python.org/2/library/queue.html#Queue.PriorityQueue) in 0.5.
