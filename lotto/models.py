##############################################################################################################
#
# by Claire Harrison (claire@softwork.co.uk)
#
# Written for django 1.9 and python 2.7
#
##############################################################################################################

from __future__ import unicode_literals
from six import with_metaclass
import decimal
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.base import ModelBase
from django.db import models

class LotteryNumbersDescriptor(object):
    '''Descriptor class to convert lottery numbers between a string for storing in the db and a list of numbers'''
    def __init__(self, field_name):
        self.field_name = field_name
    def __get__(self, instance, owner):
        val = instance.__dict__[self.field_name]
        return [int(i) for i in val.split(',')]
    def __set__(self, instance, val):
        '''Check the list of numbers in val according to the appropriate rule, sort it, and store it as a string'''
        if hasattr(instance, 'lotterytype'): instance.lotterytype.checkNumbers(val) # check numbers before saving
        else: instance.lottery.lotterytype.checkNumbers(val)
        instance.__dict__[self.field_name] = ','.join(str(i) for i in sorted(val)) # arrange numbers in ascending order

class LotteryTypeMeta(ModelBase):
    '''Metaclass to collect the names of subclasses of LotteryType as they are created.
       (They are used later in the method LotteryType.sub to find the actual class of LotteryType objects.)'''
    def __new__(cls, name, parents, dct):
        '''When creating a new class, if it is a subclass of LotteryType, lowercase its name and 
           store it in the LotteryType.subclasses class variable.'''
        if name == 'LotteryType':
            if not dct.has_key('subclasses'): dct['subclasses'] = set()
        elif 'LotteryType' in [p.__name__ for p in parents]: parents[0].subclasses.add(name.lower())
        return super(LotteryTypeMeta, cls).__new__(cls, name, parents, dct)

@python_2_unicode_compatible
class LotteryType(with_metaclass(LotteryTypeMeta, models.Model)):
    '''A series of lottery draws with the same rules, and the possibility of a rollover if no prize is allocated'''
    name = models.CharField(max_length=30)
    number_of_numbers = models.PositiveIntegerField()
    max_val = models.PositiveIntegerField()
    rollover = models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=20)
    min_matches = models.PositiveIntegerField(default=1)

    @property
    def sub(self):
        '''Return the current object as an object of its actual type (which is a subclass of LotteryType)'''
        for name in self.subclasses:
            if hasattr(self, name): return getattr(self, name)

    def __str__(self): return 'Lottery Type {}'.format(self.name)

    def checkEntry(self, e): 
        '''Check that an entry is valid.
           To be valid its numbers must be valid '''
        return self.checkNumbers(e.entry)

    def checkNumbers(self, n):
        '''Check that a list of values is valid.
           To be valid it must have the correct number of integers which must be in the range 1 to max_val (inclusive).
           And the same number should not occur more than once.
           A value Error is raised if these conditions are not met.'''
        seen = []
        if len(n) != self.number_of_numbers: raise ValueError("Incorrect number of numbers")
        for x in n: 
            if x < 1 or x > self.max_val: raise ValueError("Number out of range")
            if x in seen: raise ValueError("Duplicate Value")
            seen.append(x)
        return True

    def checkMatches(self, lottery, entry):
        '''Find how many numbers in the given entry are also in the winning_combo'''
        return len([n for n in entry.entry if n in lottery.winning_combo])

    def findWinners(self, lottery):
        return self.sub._findWinners(lottery)

    def allocatePrize(self, lottery):
        return self.sub._allocatePrize(lottery)

    # The following two static methods exist to be extended by subclasses
    @staticmethod
    def _findWinners(lottery):
        '''Find the winners of this lottery, and how many matches they have.
           Store the results in the object, and return them.
           The rule is that the punter(s) with the largest number of matches win(s) -- as long as they have at least the minimum number of matches.
           If more than one punter has the winning number of matches, they share the prize between them.'''
        lottery.maxMatches, lottery.winners = 0, set()
        for e in lottery.entry_set.all():
            matches = lottery._checkMatches(e)
           
            if matches > lottery.maxMatches: 
                lottery.maxMatches = matches
                if matches >= lottery.lotterytype.min_matches: # cant win with too few matches
                    lottery.winners = {e}
            elif matches < lottery.lotterytype.min_matches: continue
            elif matches == lottery.maxMatches: 
                lottery.winners.add(e)
        return lottery.maxMatches, lottery.winners

    @staticmethod
    def _allocatePrize(lottery):
        '''Divide the prize money (including any rollover) among the winners, if there are any winners.
           Otherwise add the prize money to the rollover.'''
        if not lottery.winners: 
            lottery.lotterytype.rollover += lottery.prize
            return None
        amount = (lottery.prize + lottery.lotterytype.rollover) / len(lottery.winners)
        lottery.lotterytype.rollover = decimal.Decimal('0.00')
        lottery.lotterytype.save()
        for w in lottery.winners: Win(entry=w, prize=amount).save()

    #class Meta:               
    #    abstract = True # dont tell django this is an abstract class, or we wont be able to use it in foreign keys

class SimpleLottery(LotteryType):
    '''A type of lottery which has a prize for the highest number of matching numbers'''
    class Meta:
        verbose_name = 'Simple Lottery Type'
        verbose_name_plural = 'Simple Lottery Types'

class MoreComplexLottery(LotteryType):
    '''A type of lottery which has a prize for the highest number of matching numbers.
       And also a prize for any entry which acheives a minimum number of matches.'''
    # additional field required to store details the extra prizes to be allocated
    spotprize_nummatches = models.PositiveIntegerField()
    spotprize_value = models.DecimalField(decimal_places=2, max_digits=20)
    
    @staticmethod
    def _findWinners(lottery):
        # the main prize
        lottery.maxMatches, lottery.winners = super(MoreComplexLottery, lottery.lotterytype.sub)._findWinners(lottery)
        # the additional prizes
        lottery.spotprize_winners = set()
        if lottery.lotterytype.sub.spotprize_nummatches < lottery.maxMatches or not lottery.winners:
            for e in [e for e in lottery.entry_set.all() if not lottery.winners or e not in lottery.winners]:
                if lottery._checkMatches(e) >= lottery.lotterytype.sub.spotprize_nummatches:
                    lottery.spotprize_winners.add(e)
        return lottery.maxMatches, lottery.winners

    @staticmethod
    def _allocatePrize(lottery):
        # the main prize
        super(MoreComplexLottery, lottery.lotterytype.sub)._allocatePrize(lottery)
        # the additional prizes
        for w in lottery.spotprize_winners: Win(entry=w, prize=lottery.lotterytype.sub.spotprize_value, wintype=Win.SPOTPRIZE).save()

    class Meta:
        verbose_name = 'More Complex Lottery Type'
        verbose_name_plural = 'More Complex Lottery Types'

@python_2_unicode_compatible
class Lottery(models.Model):
    '''A single lottery which has a specific draw date, and will eventually have a winning combination'''
    lotterytype = models.ForeignKey(LotteryType)
    drawdate = models.DateTimeField()
    prize = models.DecimalField(decimal_places=2, max_digits=20)
    _winning_combo = models.CommaSeparatedIntegerField(db_column='winning_combo', max_length=100, blank=True)
    winning_combo = LotteryNumbersDescriptor('_winning_combo') # use this field for in coding

    def __str__(self): return '{}, with draw on date {}'.format(self.lotterytype, self.drawdate)
    class Meta:
        verbose_name_plural = 'Lotteries'

    def _checkMatches(self, entry):
        return self.lotterytype.checkMatches(self, entry)

    def draw(self, *numbers):
        '''Store the winning numbers, find the winners and allocate the prize'''
        self.winning_combo = numbers
        self.save()
        self.lotterytype.findWinners(self)
        self.lotterytype.allocatePrize(self)

@python_2_unicode_compatible
class Punter(models.Model):
    '''An individual or syndicate who enters one or more lotteries'''
    name = models.CharField(max_length=100)
    password = models.BinaryField()
    def __str__(self): return self.name

@python_2_unicode_compatible
class Entry(models.Model):
    '''An entry to a lottery made by a punter'''
    punter = models.ForeignKey(Punter)
    lottery = models.ForeignKey(Lottery)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    _entry = models.CommaSeparatedIntegerField(db_column='entry', max_length=100, default=None) # this field for db storage (default=None prevents blank field being automatically stored)
    entry = LotteryNumbersDescriptor('_entry') # use this field in coding
    def __str__(self): return 'Entry by {} for lottery {}'.format(self.punter, self.lottery)
    class Meta:
        verbose_name_plural = "Entries"
        unique_together = (('punter', 'lottery'))  # dont allow punter to enter lottery more than once

@python_2_unicode_compatible
class Win(models.Model):
    '''The award of a prize for a lottery entry'''
    entry = models.OneToOneField(Entry)
    prize = models.DecimalField(decimal_places=2, max_digits=20)
    MAIN = 'M'
    SPOTPRIZE = 'S'
    wintypes = ((MAIN, 'main'), (SPOTPRIZE, 'spotprize'))
    wintype = models.CharField(max_length=1, choices=wintypes, blank=False, default=MAIN)
    def __str__(self): return 'win of {} for {}'.format(self.prize, self.entry)
