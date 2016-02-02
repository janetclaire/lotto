from django.test import TestCase
from django.db import IntegrityError
import datetime
from .models import *

class LotteryTestCase(TestCase):
    def setUp(self):
        lt = LotteryType(name = "Test Lottery", number_of_numbers = 3, max_val = 5, rollover = '0.00', min_matches=1) 
        lt.save()
        self.lottery = Lottery(lotterytype = lt, drawdate = datetime.datetime(2016,2,5,10,00), prize = '100.00')
        self.lottery.save()
    
    def testEnterNumbers(self):
        '''Test the entry of numbers for the winning combination'''
        # check that numbers are correctly converted to a string
        self.lottery.winning_combo = 1,2,3
        self.assertEqual(self.lottery._winning_combo, '1,2,3')
        # check that numbers are sorted
        self.lottery.winning_combo = 5,4,2
        self.assertEqual(self.lottery.winning_combo, [2,4,5])
        # check that too few numbers are rejected
        with self.assertRaises(ValueError):
            self.lottery.winning_combo = 1,2
        # check that too many numbers are rejected
        with self.assertRaises(ValueError):
            self.lottery.winning_combo = 1,2,3,4
        # check that duplicate numbers are rejected
        with self.assertRaises(ValueError):
            self.lottery.winning_combo = 1, 2, 1
        # check that numbers outside the range are rejected
        with self.assertRaises(ValueError):
            self.lottery.winning_combo = 4,5,6
        # check that non numeric values are rejected
        with self.assertRaises(ValueError):
            self.lottery.winning_combo = 'cat', 'dog', 'pig'


    def testMakeEntry(self):
        p = Punter(name = 'Punter 1')
        p.save()
        # check creating an entry
        e = Entry(punter=p, lottery=self.lottery)
        e.save()
        self.assertEqual(e.punter, p)
        self.assertEqual(e.lottery, self.lottery)
        # check that numbers are correctly converted to a string
        e.entry = 1,2,3
        self.assertEqual(e._entry, '1,2,3')
        # check that numbers are sorted
        e.entry = 5,4,2
        self.assertEqual(e.entry, [2,4,5])
        # check that too few numbers are rejected
        with self.assertRaises(ValueError):
            e.entry = 1,2
        # check that too many numbers are rejected
        with self.assertRaises(ValueError):
            e.entry = 1,2,3,4
        # check that duplicate numbers are rejected
        with self.assertRaises(ValueError):
            e.entry = 1, 2, 1
        # check that numbers outside the range are rejected
        with self.assertRaises(ValueError):
            e.entry = 4,5,6
        # check that non numeric values are rejected
        with self.assertRaises(ValueError):
            e.entry = 'cat', 'dog', 'pig'
        # check that same punter cannot create more than one entry
        with self.assertRaises(IntegrityError):
            e2 = Entry(punter=p, lottery=self.lottery)
            e2.save()



