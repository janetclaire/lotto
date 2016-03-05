from __future__ import unicode_literals
from django.test import TestCase
from django.db import IntegrityError
import datetime, decimal
from .models import *

class SimpleLotteryTestCase(TestCase):

    def setUp(self):
        lt = SimpleLottery(name = "Test Lottery", number_of_numbers = 3, max_val = 5, rollover = decimal.Decimal('0.00'), min_matches=1) 
        lt.save()
        self.draw = Draw(lotterytype = lt, drawdate = datetime.datetime(2016,2,5,10,00), prize = decimal.Decimal('100.00'))
        self.draw.save()
    
    def testEnterNumbers(self):
        '''Test the entry of numbers for the winning combination'''
        # check that numbers are correctly converted to a string
        self.draw.winning_combo = 1,2,3
        self.assertEqual(self.draw.db_winning_combo, '1,2,3')
        # check that numbers are sorted
        self.draw.winning_combo = 5,4,2
        self.assertEqual(self.draw.winning_combo, [2,4,5])
        # check that too few numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1,2
        # check that too many numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1,2,3,4
        # check that duplicate numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1, 2, 1
        # check that numbers outside the range are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 4,5,6
        # check that non numeric values are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 'cat', 'dog', 'pig'

    def testNoNumberEntry(self):
        ''' check that you cant save an entry without the numbers'''
        p = Punter(name = 'Punter 1', email='a@b.cd')
        p.save()
        e = Entry(punter=p, draw=self.draw)
        with self.assertRaises(IntegrityError):
            e.save()

    def testMakeEntry(self):
        ''' check that valid entries are accepted and invalid rejected'''
        p = Punter(name = 'Punter 1', email='a@b.cd')
        p.save()
        # check creating an entry
        e = Entry(punter=p, draw=self.draw)
        e.entry = 1,2,3
        e.save()
        self.assertEqual(e.punter, p)
        self.assertEqual(e.draw, self.draw)
        # check that numbers are correctly converted to a string
        e.entry = 1,2,3
        self.assertEqual(e.db_entry, '1,2,3')
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

    def testDuplicateEntry(self):
        ''' check that same punter cannot create more than one entry'''
        p = Punter(name = 'Punter 1', email='a@b.cd')
        p.save()
        e = Entry(punter=p, draw=self.draw)
        e.entry = 3,4,5
        e.save()
        with self.assertRaises(IntegrityError):
            e2 = Entry(punter=p, draw=self.draw)
            e2.entry = 3,4,5
            e2.save()

    def testEnterNumbers(self):
        '''Test the entry of numbers for the winning combination'''
        # check that numbers are correctly converted to a string
        self.draw.winning_combo = 1,2,3
        self.assertEqual(self.draw.db_winning_combo, '1,2,3')
        # check that numbers are sorted
        self.draw.winning_combo = 5,4,2
        self.assertEqual(self.draw.winning_combo, [2,4,5])
        # check that too few numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1,2
        # check that too many numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1,2,3,4
        # check that duplicate numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1, 2, 1
        # check that numbers outside the range are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 4,5,6
        # check that non numeric values are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 'cat', 'dog', 'pig'

class SimpleLotteryResultTestCase(TestCase):

    def setUp(self):
        lt = SimpleLottery(name = "Test Lottery", number_of_numbers = 3, max_val = 10, rollover = decimal.Decimal('0.00'), min_matches=1) 
        lt.save()
        self.draw = Draw(lotterytype = lt, drawdate = datetime.datetime(2016,2,5,10,00), prize = decimal.Decimal('100.00'))
        self.draw.save()
        p1 = Punter(name = 'Punter 1', email='a@b.cd')
        p1.save()
        self.e1 = Entry(punter=p1, draw=self.draw, db_entry='1,2,3')
        self.e1.save()
        p2 = Punter(name = 'Punter 2', email='b@b.cd')
        p2.save()
        self.e2 = Entry(punter=p2, draw=self.draw, db_entry='2,3,4')
        self.e2.save()
        p3 = Punter(name = 'Punter 3', email='c@b.cd')
        p3.save()
        self.e3 = Entry(punter=p3, draw=self.draw, db_entry='1,3,4')
        self.e3.save()

    def testDraw(self):
        '''test the draw, and allocation of prizes'''
        # test that the correct winning entries are found
        self.draw.makeDraw(2,3,5)
        winning_entries = self.draw.entry_set.filter(win__isnull=False) # use the orm to read the winning entries
        self.assertEqual(len(winning_entries), 2)
        self.assertIn(self.e1, winning_entries)
        self.assertIn(self.e2, winning_entries)
        # test that the prize allocated is correct
        self.assertEqual(winning_entries[0].win.prize, self.draw.prize/2)
        self.assertEqual(winning_entries[1].win.prize, self.draw.prize/2)

    def testNoWin(self):
        '''test that if the conditions for a win are not met, no winning entries are selected, and the prize is rolled over'''
        self.draw.makeDraw(6,7,8)
        winning_entries = self.draw.entry_set.filter(win__isnull=False) # use the orm to read the winning entries
        # test that there are no winners
        self.assertEqual(len(winning_entries), 0)
        # test that the prize money has rolled over
        self.assertEqual(self.draw.prize, self.draw.lotterytype.rollover)

    def testRolloverAllocated(self):
        '''test that when there is a rollover it is correctly applied and then reset'''
        # set the rollover
        self.draw.lotterytype.rollover = decimal.Decimal(1000)
        self.draw.lotterytype.save()
        self.assertEqual(self.draw.lotterytype.rollover, decimal.Decimal(1000.00))
        # do the draw
        self.draw.makeDraw(1,2,3)
        winning_entries = self.draw.entry_set.filter(win__isnull=False) # use the orm to read the winning entries
        # test that there is one winning entry
        self.assertEqual(len(winning_entries), 1)
        # test that the rollover has been added to the prize money allocated
        self.assertEqual(winning_entries[0].win.prize, self.draw.prize+decimal.Decimal(1000.00))
        # test that the rollover has been reset
        self.assertEqual(self.draw.lotterytype.rollover, decimal.Decimal(0.00))

class MoreComplexLotteryTestCase(TestCase):

    def setUp(self):
        lt = MoreComplexLottery(name = "Test Lottery", number_of_numbers = 3, max_val = 5, rollover = decimal.Decimal('0.00'), min_matches=1, spotprize_nummatches=3, spotprize_value=decimal.Decimal('10.00'))
        lt.save()
        self.draw = Draw(lotterytype = lt, drawdate = datetime.datetime(2016,2,5,10,00), prize = decimal.Decimal('100.00'))
        self.draw.save()
    
    def testEnterNumbers(self):
        '''Test the entry of numbers for the winning combination'''
        # check that numbers are correctly converted to a string
        self.draw.winning_combo = 1,2,3
        self.assertEqual(self.draw.db_winning_combo, '1,2,3')
        # check that numbers are sorted
        self.draw.winning_combo = 5,4,2
        self.assertEqual(self.draw.winning_combo, [2,4,5])
        # check that too few numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1,2
        # check that too many numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1,2,3,4
        # check that duplicate numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1, 2, 1
        # check that numbers outside the range are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 4,5,6
        # check that non numeric values are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 'cat', 'dog', 'pig'

    def testNoNumberEntry(self):
        ''' check that you cant save an entry without the numbers'''
        p = Punter(name = 'Punter 1', email='a@b.cd')
        p.save()
        e = Entry(punter=p, draw=self.draw)
        with self.assertRaises(IntegrityError):
            e.save()

    def testMakeEntry(self):
        ''' check that valid entries are accepted and invalid rejected'''
        p = Punter(name = 'Punter 1', email='a@b.cd')
        p.save()
        # check creating an entry
        e = Entry(punter=p, draw=self.draw)
        e.entry = 1,2,3
        e.save()
        self.assertEqual(e.punter, p)
        self.assertEqual(e.draw, self.draw)
        # check that numbers are correctly converted to a string
        e.entry = 1,2,3
        self.assertEqual(e.db_entry, '1,2,3')
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

    def testDuplicateEntry(self):
        ''' check that same punter cannot create more than one entry'''
        p = Punter(name = 'Punter 1', email='a@b.cd')
        p.save()
        e = Entry(punter=p, draw=self.draw)
        e.entry = 3,4,5
        e.save()
        with self.assertRaises(IntegrityError):
            e2 = Entry(punter=p, draw=self.draw)
            e2.entry = 3,4,5
            e2.save()

    def testEnterNumbers(self):
        '''Test the entry of numbers for the winning combination'''
        # check that numbers are correctly converted to a string
        self.draw.winning_combo = 1,2,3
        self.assertEqual(self.draw.db_winning_combo, '1,2,3')
        # check that numbers are sorted
        self.draw.winning_combo = 5,4,2
        self.assertEqual(self.draw.winning_combo, [2,4,5])
        # check that too few numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1,2
        # check that too many numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1,2,3,4
        # check that duplicate numbers are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 1, 2, 1
        # check that numbers outside the range are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 4,5,6
        # check that non numeric values are rejected
        with self.assertRaises(ValueError):
            self.draw.winning_combo = 'cat', 'dog', 'pig'

class MoreComplexLotteryResultTestCase(TestCase):

    def setUp(self):
        lt = MoreComplexLottery(name = "Test Lottery", number_of_numbers = 3, max_val = 10, rollover = decimal.Decimal('0.00'), min_matches=1, spotprize_nummatches=1, spotprize_value=decimal.Decimal('10.00')) 
        lt.save()
        self.draw = Draw(lotterytype = lt, drawdate = datetime.datetime(2016,2,5,10,00), prize = decimal.Decimal('100.00'))
        self.draw.save()
        p1 = Punter(name = 'Punter 1', email='a@b.cd')
        p1.save()
        self.e1 = Entry(punter=p1, draw=self.draw, db_entry='1,2,3')
        self.e1.save()
        p2 = Punter(name = 'Punter 2', email='b@b.cd')
        p2.save()
        self.e2 = Entry(punter=p2, draw=self.draw, db_entry='2,3,4')
        self.e2.save()
        p3 = Punter(name = 'Punter 3', email='c@c.cd')
        p3.save()
        self.e3 = Entry(punter=p3, draw=self.draw, db_entry='1,3,4')
        self.e3.save()

    def testDraw(self):
        '''test the draw, and allocation of prizes'''
        # test that the correct winning entries are found
        self.draw.makeDraw(2,3,5)
        # new we have 2 winners of the main prize, who get 50 each, and one winner of the spot prize who gets 10
        winning_entries = self.draw.entry_set.filter(win__isnull=False) # use the orm to read the winning entries
        self.assertEqual(len(winning_entries), 3)
        self.assertIn(self.e1, winning_entries)
        self.assertEqual(self.e1.win.wintype, Win.MAIN)
        self.assertEqual(self.e1.win.prize, decimal.Decimal('50.00'))
        self.assertIn(self.e2, winning_entries)
        self.assertEqual(self.e2.win.wintype, Win.MAIN)
        self.assertEqual(self.e2.win.prize, decimal.Decimal('50.00'))
        self.assertIn(self.e3, winning_entries)
        self.assertEqual(self.e3.win.wintype, Win.SPOTPRIZE)
        self.assertEqual(self.e3.win.prize, decimal.Decimal('10.00'))

    def testNoWin(self):
        '''test that if the conditions for a win are not met, no winning entries are selected, and the prize is rolled over'''
        self.draw.makeDraw(6,7,8)
        winning_entries = self.draw.entry_set.filter(win__isnull=False) # use the orm to read the winning entries
        # test that there are no winners
        self.assertEqual(len(winning_entries), 0)
        # test that the prize money has rolled over
        self.assertEqual(self.draw.prize, self.draw.lotterytype.rollover)

    def testRolloverAllocated(self):
        '''test that when there is a rollover it is correctly applied and then reset'''
        # set the rollover
        self.draw.lotterytype.rollover = decimal.Decimal(1000)
        self.draw.lotterytype.save()
        self.assertEqual(self.draw.lotterytype.rollover, decimal.Decimal(1000.00))
        # do the draw
        self.draw.makeDraw(1,2,3)
        winning_entries = self.draw.entry_set.filter(win__isnull=False, win__wintype=Win.MAIN) # use the orm to read the winning entries for the main prize
        # test that there is one winning entry for the main prize
        self.assertEqual(len(winning_entries), 1)
        # test that the rollover has been added to the prize money allocated
        self.assertEqual(winning_entries[0].win.prize, self.draw.prize+decimal.Decimal(1000.00))
        # test that the rollover has been reset
        self.assertEqual(self.draw.lotterytype.rollover, decimal.Decimal(0.00))
