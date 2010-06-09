"""Channel testing"""
from test.testlib import *
from git.async.channel import *

import time

class TestChannels(TestBase):
	
	def test_base(self):
		# creating channel yields a write and a read channal
		wc, rc = mkchannel()
		assert isinstance(wc, WChannel)		# default args
		assert isinstance(rc, RChannel)
		
		
		# TEST UNLIMITED SIZE CHANNEL - writing+reading is FIFO
		item = 1
		item2 = 2
		wc.write(item)
		wc.write(item2)
		
		# read all - it blocks as its still open for writing
		to = 0.2
		st = time.time()
		assert rc.read(timeout=to) == [item, item2]
		assert time.time() - st >= to
		
		# next read blocks. it waits a second
		st = time.time()
		assert len(rc.read(1, True, to)) == 0
		assert time.time() - st >= to
		
		# writing to a closed channel raises
		assert not wc.closed()
		wc.close()
		assert wc.closed()
		wc.close()	# fine
		assert wc.closed()
		
		self.failUnlessRaises(ReadOnly, wc.write, 1)
		
		# reading from a closed channel never blocks
		assert len(rc.read()) == 0
		assert len(rc.read(5)) == 0
		assert len(rc.read(1)) == 0
		
		
		# test callback channels
		wc, rc = mkchannel(wctype = CallbackWChannel, rctype = CallbackRChannel)
		
		cb = [0, 0]		# set slots to one if called
		def pre_write(item):
			cb[0] = 1
			return item + 1
		def pre_read(count):
			cb[1] = 1
			
		# set, verify it returns previous one
		assert wc.set_pre_cb(pre_write) is None
		assert rc.set_pre_cb(pre_read) is None
		assert wc.set_pre_cb(pre_write) is pre_write
		assert rc.set_pre_cb(pre_read) is pre_read
		
		# writer transforms input
		val = 5
		wc.write(val)
		assert cb[0] == 1 and cb[1] == 0
		
		rval = rc.read(1)[0]		# read one item, must not block
		assert cb[0] == 1 and cb[1] == 1
		assert rval == val + 1
		
		
