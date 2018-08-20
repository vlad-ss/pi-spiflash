#!/usr/bin/env python

import spidev
import time
from time import sleep
import sys

h_ZERO = 0x00
h_ONES = 0xFF

# Base commands
h_WRITE_ENABLE = 0x06
h_WRITE_DISABLE = 0x04
h_READ_STAT_REG = 0x05
h_WRITE_STAT_REG = 0x01
h_READ_DATA = 0x03
h_FAST_READ = 0x0B
h_PAGE_PROGRAM = 0x02
h_SECTOR_ERASE = 0x20
h_BLOCK_ERASE = 0xD8
h_BLOCK_ERASE_2 = 0x52
h_CHIP_ERASE = 0xC7
h_CHIP_ERASE_2 = 0x60
h_DEEP_POWERDOWN = 0xB9
h_RELEASE_DEEP_PD = 0xAB
h_DEVICE_ID = 0x90
h_READ_ID = 0x9F
h_ENTER_OTP = 0x3A
h_EXIT_OTP = 0x04

# == Base functions ==

# Connect spi to device
def connect(bus = 0, device = 0):
        spi = spidev.SpiDev(bus, device)
        spi.open(bus, device)
        return spi

# Configure spi
def configure(spi, max_speed_hz = 1953125, mode = 0, bits_per_word = 8):
        spi.max_speed_hz = max_speed_hz
        spi.mode = mode
        spi.bits_per_word = bits_per_word

def print_configuration(spi):
        print "max_speed_hz: %s" % spi.max_speed_hz
        print "mode: %s" % spi.mode
        print "bits_per_word: %s" % spi.bits_per_word

# Set CS# (Chip Select) in different states
def cs_high_low(spi):
        spi.cshigh = True;
        spi.cshigh = False;

def cs_low_high(spi):
        spi.cshigh = False;
        spi.cshigh = True;

def cs_low(spi):
        spi.cshigh = False;

def cs_high(spi):
        spi.cshigh = True;

# Send 1 Byte into device
def transfer(spi, byte):
        return spi.xfer([byte])[0]

# Wait for device to became free
def wait_for_device(spi):
        transfer(spi, h_READ_STAT_REG)
        while(transfer(spi, h_ZERO) & 0x01 == 1):
                print(".")

def write_in_progress(spi):
	while(spi.xfer2([h_READ_STAT_REG, h_ZERO])[1] & 0x01 == 1):
		sleep(0.001)

# Write Enable
def write_enable(spi):
	spi.xfer2([h_WRITE_ENABLE])

# Write Disable
def write_disable(spi):
	spi.xfer2([h_WRITE_DISABLE])

# Read Status Register
def read_status_register(spi):
	return spi.xfer2([h_READ_STAT_REG, h_ZERO])[1]

# Write Status Register
def write_status_register(spi, hStatReg):
	spi.xfer2([h_WRITE_STAT_REG, hStatReg])

# Read Data Bytes
def read_data(spi, addr3, addr2, addr1):
	scmd = [h_READ_DATA, addr3, addr2, addr1] + [h_ONES for _ in range(256)];
	data = spi.xfer2(scmd)[4:]
	return data

# Page Program
def page_program(spi, addr3, addr2, addr1, data):
	scmd = [h_PAGE_PROGRAM, addr3, addr2, addr1] + data
	spi.xfer2(scmd)

# Sector Erase
def sector_erase(spi, addr3, addr2, addr1):
	spi.xfer2([h_SECTOR_ERASE, addr3, addr2, addr1])

# Block Erase
def block_erase(spi, addr3, addr2, addr1):
	spi.xfer2([h_BLOCK_ERASE, addr3, addr2, addr1])

# Chip Erase
def chip_erase(spi):
	spi.xfer2([h_CHIP_ERASE])

# Read ID
def read_id(spi):
	return spi.xfer2([h_READ_ID, h_ZERO, h_ZERO, h_ZERO])[1:]

# == Formatted output ==

# Hex Page Out
def hex_page_out(data):
	j = 1
	for i in data:
		sys.stdout.write('%02X ' % i)
		if j % 32 == 0:
			print('')
		elif j % 4 == 0:
			sys.stdout.write('| ')
		sys.stdout.flush()
		j = j + 1

# Hex Page Out as hex array
def hex_page_out_array(data):
	for i in data:
		sys.stdout.write('0x%02X, ' % i)
	sys.stdout.flush()

# Hex Page Out with Addresses
def hex_page_out_addr(data, addr3, addr2):
	j = 1
	sys.stdout.write('%02X.%02X.00:  ' % (addr3, addr2))
	for i in data:
		sys.stdout.write('%02X ' % i)
		if j % 32 == 0:
			print('')
			if j < 256:
				sys.stdout.write('%02X.%02X.%02X:  ' % (addr3, addr2, j))
		elif j % 4 == 0:
			sys.stdout.write('| ')
		sys.stdout.flush()
		j = j + 1

# == Big Functions ==

# Read Page with out
def ReadPage(spi, addr3, addr2):
	print('Page 0x%02X.%02X.00:' % (addr3, addr2))
	hex_page_out(read_data(spi, addr3, addr2, h_ZERO))

# Read Page with out (addressed)
def ReadPageAddr(spi, addr3, addr2):
	hex_page_out_addr(read_data(spi, addr3, addr2, h_ZERO), addr3, addr2)

# Read Page with out (array)
def ReadPageArray(spi, addr3, addr2):
	hex_page_out_array(read_data(spi, addr3, addr2, h_ZERO))

def ReadSector(spi, addr3, addr2):
	ReadPageAddr(spi, addr3, addr2)
	ReadPageAddr(spi, addr3, addr2 + 0x01)
	ReadPageAddr(spi, addr3, addr2 + 0x02)
	ReadPageAddr(spi, addr3, addr2 + 0x03)
	ReadPageAddr(spi, addr3, addr2 + 0x04)
	ReadPageAddr(spi, addr3, addr2 + 0x05)
	ReadPageAddr(spi, addr3, addr2 + 0x06)
	ReadPageAddr(spi, addr3, addr2 + 0x07)
	ReadPageAddr(spi, addr3, addr2 + 0x08)
	ReadPageAddr(spi, addr3, addr2 + 0x09)
	ReadPageAddr(spi, addr3, addr2 + 0x0A)
	ReadPageAddr(spi, addr3, addr2 + 0x0B)
	ReadPageAddr(spi, addr3, addr2 + 0x0C)
	ReadPageAddr(spi, addr3, addr2 + 0x0D)
	ReadPageAddr(spi, addr3, addr2 + 0x0E)
	ReadPageAddr(spi, addr3, addr2 + 0x0F)

def ReadSectorArray(spi, addr3, addr2):
	ReadPageArray(spi, addr3, addr2)
	ReadPageArray(spi, addr3, addr2 + 0x01)
	ReadPageArray(spi, addr3, addr2 + 0x02)
	ReadPageArray(spi, addr3, addr2 + 0x03)
	ReadPageArray(spi, addr3, addr2 + 0x04)
	ReadPageArray(spi, addr3, addr2 + 0x05)
	ReadPageArray(spi, addr3, addr2 + 0x06)
	ReadPageArray(spi, addr3, addr2 + 0x07)
	ReadPageArray(spi, addr3, addr2 + 0x08)
	ReadPageArray(spi, addr3, addr2 + 0x09)
	ReadPageArray(spi, addr3, addr2 + 0x0A)
	ReadPageArray(spi, addr3, addr2 + 0x0B)
	ReadPageArray(spi, addr3, addr2 + 0x0C)
	ReadPageArray(spi, addr3, addr2 + 0x0D)
	ReadPageArray(spi, addr3, addr2 + 0x0E)
	ReadPageArray(spi, addr3, addr2 + 0x0F)
	print('')

# Write Page with out
def WritePage(spi, addr3, addr2, data):
	print('Page 0x%02X.%02X.00 writing: ' % (addr3, addr2)),
	write_enable(spi)
	page_program(spi, addr3, addr2, h_ZERO, data)
	write_in_progress(spi)
	print('Done')

# Write Page Semi Silent
def WritePageSemiSil(spi, addr3, addr2, data):
	write_enable(spi)
	page_program(spi, addr3, addr2, h_ZERO, data)
	write_in_progress(spi)

# Sector Erase with out
def SectorErase(spi, addr3, addr2):
	print('Sector 0x%02X.%02X.00 erasing: ' % (addr3, addr2)),
	write_enable(spi)
	sector_erase(spi, addr3, addr2, h_ZERO)
	write_in_progress(spi)
	print('Done')

# Sector Erase SemiSilent
def SectorEraseSemiSil(spi, addr3, addr2):
	write_enable(spi)
	sector_erase(spi, addr3, addr2, h_ZERO)
	write_in_progress(spi)

# Block Erase with out
def BlockErase(spi, addr3):
	print('Block 0x%02X.00.00 erasing: ' % (addr3)),
	write_enable(spi)
	sector_erase(spi, addr3, h_ZERO, h_ZERO)
	write_in_progress(spi)
	print('Done')

# Chip Erase with out
def ChipErase(spi):
	print('Chip erasing: '),
	write_enable(spi)
	chip_erase(spi)
	write_in_progress(spi)
	print('Done')

# Read Stat. Reg. with out
def ReadStatReg(spi):
	print('Stat. Reg. = {0:#010b}'.format(read_status_register(spi)))

# Read ID with out
def ReadID(spi):
	flid = read_id(spi)
	print('ID = %02X %02X%02X' % (flid[0], flid[1], flid[2]))
