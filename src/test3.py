import simpy

def test_condition(env):
    t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
    ret = yield t1 | t2
    assert ret == {t1: 'spam'}
    t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
    ret = yield t1 & t2
    assert ret == {t1: 'spam', t2: 'eggs'}
    # You can also concatenate & and |
    e1, e2, e3 = [env.timeout(i) for i in range(3)]
    yield (e1 | e2) & e3
    assert all(e.processed for e in [e1, e2, e3])

from SimPyStuff import *


def producer(name, env, store, time):
    for i in range(100):
        yield env.timeout(time)
        store.dropPut('%s spam %s' % (name,i))
        print('%s produced spam %d at' % (name,i), env.now, "and have %s " % str(store.items))


def consumer(name, env, store):
    while True:
        yield env.timeout(1)
        print(name, 'requesting spam at', env.now)
        item = yield store.get()
        print(name, 'got', item, 'at', env.now)

def multi_consumer(name, env, store1, store2):
    while True:
        yield env.timeout(2)
        print(name, 'requesting spam at', env.now)

        g1, g2 = store1.get(), store2.get()

        items = yield g1 | g2

        item1 = 'nothing'
        item2 = 'nothing'

        if g1 in items:
            item1 = items[g1]
        else: g1.cancel() # Otherwise, the item is removed anyway, but isn't returned anywhere.

        if g2 in items:
            item2 = items[g2]
        else: g2.cancel() # Otherwise, the item is removed anyway, but isn't returned anywhere.

        print name, 'got', item1, 'and', item2, 'at', env.now

# This does NOT work.  Cancelling does nothing in this situation.
def timid_consumer(name, env, store):
    while True:
        yield env.timeout(1)
        print(name, 'requesting spam at', env.now)
        event = store.get()
        item = yield event
        print(name, 'got', item, 'at', env.now)
        event.cancel()
        print(name, 'cancelled')

def spawner(env, cb, arg):

    while True:
        yield env.process(cb(arg))


def callback(arg):
    yield simpy.Timeout(arg)
    print 'made it'
    env.exit()

env = simpy.Environment(src.SimPyStuff.trace_cb)
#sp = env.process(spawner(env, callback, 5))

store1 = DropStore(env, capacity=2)
# store2 = DropStore(env, capacity=2)
prod1 = env.process(producer("p1", env, store1,3))
# prod2 = env.process(producer("p2", env, store2,2))
#prods = [env.process(producer(i, env, store)) for i in range(2)]
consumers = [env.process(consumer(i, env, store1)) for i in range(1)]
#mc = env.process(multi_consumer(0, env, store1, store2))
#tc = env.process(timid_consumer(0, env, store1))
env.run(until=15)