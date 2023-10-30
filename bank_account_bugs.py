"""Buggy bank account.  

Select a bug using environment variable TESTCASE with value 0 ... 7.
"""
import os
from money import Money
from check import Check

# Constants for errors

# cannot withdraw exactly available amount
BUG_CANT_WITHDRAW_AVAILABLE = 1
# over-withdraw returns None instead of raising exception
BUG_WITHDRAW_FAILS_SILENTLY = 2
# can deposit money with value 0
BUG_DEPOSIT_ZERO = 3
# can clear any check (no exception raised)
BUG_CLEAR_ANY_CHECK = 4
# can deposit a check more than once
BUG_DUPLICATE_CHECK = 5
# can deposit anyone's check (payee name not same as account name)
BUG_DEPOSIT_ANY_PAYEE = 6
# value of uncleared checks is not included in total balance
BUG_BALANCE_EXCLUDES_HOLDS = 7
# no bugs
NO_DEFECTS = 8
# available balance computed incorrectly when check is on hold
BUG_AVAILABLE_BALANCE = 9
# the minimum balance requirement is not enforced. Can withdraw everything.
BUG_MINIMUM_IS_IGNORED = 10
# The actual test case, set in BankAccount using an envvar
TESTCASE = 0

def bug(index: int) -> bool:
    return index == TESTCASE


def config(envvar, default="", cast=None):
    """Like decouple.config, read a variable from the environment, 
    with optional casting.  This is so we don't require the decouple package.
    """
    value = os.getenv(envvar)
    if not value and default:
        value = default
    if value and cast:
        return cast(value)
    return value


class BankAccount:
    """
    A BankAccount that accepts deposits of Money or Checks and withdraw of money.

    A BankAccount has a balance and may have a minimum required balance (default 0).
    The balance is always the total value of money and checks in the account, 
    but the value of a check is not available for withdraw until 
    `clear_check(check)` is called to "clear" the check.
    The "available balance" is the maximum that can be withdrawn.
    Available balance is the total balance minus the value of uncleared
    checks and any minimum balance requirement.
    """

    def __init__(self, name: str, min_balance: float = 0.0):
        """Create a new account with given name.

        :param name: the name of the account owner 
        :min_balance: the minimum required balance, a non-negative number.
                Default min balance is zero.
        """
        # you don't need to test min_balance < 0. It's too trivial.
        assert min_balance >= 0, "min balance parameter must not be negative"
        self.__name = name
        self.__balance = 0.0
        self.__min_balance = float(min_balance)
        # checks deposited and waiting to be cleared
        self.__pending_checks = []
        self.__deposited_checks = []
        # variable for which bug to use
        global TESTCASE
        TESTCASE = int(os.getenv('TESTCASE','0'))
    
    @property
    def account_name(self):
        """The account owner name."""
        return self.__name
    
    @property
    def available(self) -> float:
        """Available balance in this account (float), as a read-only property.
        
        Available balance is the maximum that can be withdrawn without either:
        (a) balance becoming less than min_balance, or
        (b) balance being less than the value of uncleared checks.
        """
        sum_holds = sum(check.value for check in self.__pending_checks)
        # the held-back amount is max of min_balance or sum of uncleared checkes
        if bug(BUG_AVAILABLE_BALANCE):
            # available balance computed incorrectly
            avail = self.__balance - self.min_balance - sum_holds
        elif bug(BUG_MINIMUM_IS_IGNORED):
            # no minimum balance requirement
            avail = self.__balance - sum_holds
        else:
            avail = self.__balance - max(self.min_balance, sum_holds)
        return avail if (avail>0) else 0.0
    
    @property
    def balance(self) -> float:
        """Balance in this account (float), as a read-only property"""
        if bug(BUG_BALANCE_EXCLUDES_HOLDS):
            # exclude non-cleared checks from balance
            hold_amount = sum([chk.value for chk in self.__pending_checks])
        else:
            hold_amount = 0
        return self.__balance - hold_amount

    def clear_check(self, check: Check):
        """Mark a check as cleared so it is available for withdraw.

        :param check: reference to a previously deposited check.
        :raises CheckError: if the check is not in the list of uncleared checks.
        """
        if check in self.__pending_checks:
            self.__pending_checks.remove(check)
        elif not bug(BUG_CLEAR_ANY_CHECK):
            raise CheckError(f"Check {check.check_number} is not an uncleared check")
    
    def deposit(self, money: Money):
        """Deposit money or check into the account. 
        
        :param money: Money or Check object with a positive value.
        :raises ValueError: if value of money parameter is not positive.
        :raises TypeError: if the parameter is not money.
        :raises CheckError: if param is a check that cannot be deposited.
        """
        if money.value <= 0:
            if money.value == 0 and bug(BUG_DEPOSIT_ZERO):
                # Bug: Allow deposit of 0
                pass
            else:
                raise ValueError("Value to deposit must be positive.")
        # if it is a check, verify the check was not already deposited
        if isinstance(money, Check):
            check = money
            if check.payee and check.payee.lower() != self.account_name.lower():
                # account owner is not the check payee
                if not bug(BUG_DEPOSIT_ANY_PAYEE):
                    raise CheckError(f"Check payee {check.payee} is not account owner")
            if check in self.__deposited_checks:
                if not bug(BUG_DUPLICATE_CHECK):
                    raise CheckError("Check already deposited")
            # add to list of checking waiting to clear
            self.__pending_checks.append(check)
            self.__deposited_checks.append(check)
        # both cash and checks contribute to the balance
        self.__balance += money.value
    
    @property
    def min_balance(self) -> float:
        """Minimum required balance for this account, read-only."""
        return self.__min_balance
    
    def withdraw(self, amount: float) -> Money:
        """Withdraw an amount from the account. 

        :param amount: (number) the amount to withdraw, at most the available balance.
        :returns: a Money object for the amount requested, using the default currency.
        :raises ValueError: if amount exceeds available balance or is not positive.
        """
        if amount <= 0:
            raise ValueError("Amount to withdraw must be positive") 
        if amount > self.available:
            if bug(BUG_WITHDRAW_FAILS_SILENTLY):
                return None
            raise ValueError(f"Amount exceeds available balance")
        if amount == self.available and bug(BUG_CANT_WITHDRAW_AVAILABLE):
            # bug: you cannot withdraw exactly the available balance 
            raise ValueError(f"Amount exceeds available balance")
        # try to create the money before deducting from balance,
        # in case Money throws an exception.
        money = Money(amount)
        self.__balance -= amount
        return money
    
    def __str__(self):
        """String representation of the bank account."""
        return f"{self.account_name} Account"


class CheckError(Exception):
    """Exception raised by invalid operations on checks."""
    # all behavior is inherited from the superclass
    pass
