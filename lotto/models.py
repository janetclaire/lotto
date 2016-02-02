##############################################################################################################
#
# by Claire Harrison (claire@softwork.co.uk)
#
# Written for django 1.9 and python 2.7
#
##############################################################################################################

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

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

@python_2_unicode_compatible
class LotteryType(models.Model):
    '''A series of lottery draws with the same rules, and the possibility of a rollover if no prize is allocated'''
    name = models.CharField(max_length=30)
    number_of_numbers = models.PositiveIntegerField()
    max_val = models.PositiveIntegerField()
    rollover = models.DecimalField(decimal_places=2, default='0.00', max_digits=20)
    min_matches = models.PositiveIntegerField(default=1)

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

@python_2_unicode_compatible
class Lottery(models.Model):
    '''A single lottery which has a draw date, and will eventually have a winning combination'''
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

    def findWinners(self):
        '''Find the winners of this lottery, and how many matches they have.
           Store the results in the object, and return them.
           The rule is that the punter(s) with the largest number of matches win(s) -- as long as they have at least the minimum number of matches.
           If more than one punter has the winning number of matches, they share the prize between them.'''
        self.maxMatches, self.winners = 0, None
        for e in self.entry_set.all():
            matches = self._checkMatches(e)
            if matches < self.lotteryType.min_matches: continue # cant win with too few matches
            elif matches > self.maxMatches: 
                self.winners = {e}
                self.maxMatches = matches
            elif matches == self.maxMatches: 
                self.winners.add(e)
                self.maxMatches = matches
        return self.maxMatches, self.winners

    def allocatePrize(self):
        '''Divide the prize money (including any rollover) among the winners, if there are any winners.
           Otherwise add the prize money to the rollover.'''
        if not self.winners: 
            self.lotteryType.rollover += self.prize
            return None
        amount = (self.prize + self.lotterytype.rollover) / len(self.winners)
        self.lotterytype.rollover = '0.00'
        self.lotterytype.save()
        for w in self.winners: Win(entry=w, prize=amount).save()

@python_2_unicode_compatible
class Punter(models.Model):
    '''An individual or syndicate who enters the lottery'''
    name = models.CharField(max_length=100)
    password = models.BinaryField()
    def __str__(self): return self.name

@python_2_unicode_compatible
class Entry(models.Model):
    '''An entry to a lottery made by a punter'''
    punter = models.ForeignKey(Punter)
    lottery = models.ForeignKey(Lottery)
    time = models.DateTimeField(auto_now_add = True)
    _entry = models.CommaSeparatedIntegerField(db_column='entry', max_length=100, blank=False) # this field for db storage
    entry = LotteryNumbersDescriptor('_entry') # use this field in coding
    def __str__(self): return 'Entry by {} for lottery {}'.format(self.punter, self.lottery)
    class Meta:
        verbose_name_plural = "Entries"
        unique_together = (('punter', 'lottery'))  # dont allow punter to enter lottery more than once

@python_2_unicode_compatible
class Win(models.Model):
    '''The award of a prize for a lottery entry'''
    entry = models.ForeignKey(Entry)
    prize = models.DecimalField(decimal_places=2, max_digits=20)
    def __str__(self): return 'win of {} for {}'.format(self.prize, self.entry)
