import smbus
import time
 
class display:
    def __init__(self, i2cbus=1, addr=0x3e):
        self.i2c = smbus.SMBus(i2cbus)
        self.addr = addr
        self.i2c.write_byte_data(self.addr, 0, 0x38)
        self.i2c.write_byte_data(self.addr, 0, 0x39)
        self.i2c.write_byte_data(self.addr, 0, 0x14)
        self.i2c.write_byte_data(self.addr, 0, 0x7e)
        self.i2c.write_byte_data(self.addr, 0, 0x55)
        self.i2c.write_byte_data(self.addr, 0, 0x6c)
        time.sleep(0.2)
        self.i2c.write_byte_data(self.addr, 0, 0x0c)
        self.clear()
 
    def clear(self):
        self.i2c.write_byte_data(self.addr, 0, 0x01)
        time.sleep(0.002)
 
    def put(self, msg):
        self.i2c.write_i2c_block_data(self.addr, 0x40, list(map(ord, msg)) )
 
    def pos(self, low, col):
        self.i2c.write_byte_data(self.addr, 0, 0x80 | (0x40 if low > 0 else 0) | col)
