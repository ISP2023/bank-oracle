#!/bin/bash

TESTMODULE="test_bank_account.py"

if [ ! -f $TESTMODULE ]; then
	echo "No tests code $TESTMODULE"
	exit 9
fi

# arrays to record results. Elements are appended in runtests()
expect=("")
actual=("")

# Target and variants
TARGET=bank_account.py
GOOD_CODE=oracle/bank_account_bugs.py
BUG_CODE=oracle/bank_account_bugs.py

drawline( ) {
    echo "----------------------------------------------------------------------"
}
runtests( ) {
    if [ ! -f $GOOD_CODE ]; then
        echo "No file ${GOOD_CODE}"
        exit 1
    fi
    if [ ! -f $BAD_CODE ]; then
        echo "No file ${BAD_CODE}"
        exit 1
    fi
	# backup student file
	if [ ! -f bank_account_orig.py ]; then
		cp $TARGET bank_account_orig.py
	fi
	for testcase in 1 2 3 4 5 6 7 8; do
        echo ""
        drawline
        # append new element to expect. All testcases should fail except one.
        expect+=("FAIL")
		case $testcase in
    	8)
			echo "BankAccount #8: All methods work according to specification. Tests should PASS."
			#/bin/cp $GOOD_CODE $TARGET
			/bin/cp $BUG_CODE $TARGET
			expect[8]="OK"
       		;;
    	*)
			echo "BankAccount #{testcase}: Some defect in code. At least one test should FAIL."
			/bin/cp $BUG_CODE  $TARGET
			;;
		esac
        drawline
		export TESTCASE=$testcase
		python3 -m unittest -v $TESTMODULE
		# record status
		if [ $? -eq 0 ]; then
			actual+=("OK")
		else
			actual+=("FAIL")
		fi
		# wait til user presses enter
		#read input
	done
}

showresults() {
    drawline
    echo "Results of Testing All Bank Account Codes"
    drawline
    echo "OK=all tests pass, FAIL=some tests fail"
    echo ""
    echo " Code#   Expected  Actual"
    failures=0
    
	for testcase in ${!expect[@]}; do
        # didn't use element 0
        if [ $testcase -eq 0 ]; then continue; fi
        printf "%4d      %-4s     %s\n" ${testcase} ${expect[$testcase]} ${actual[$testcase]}
        if [ ${expect[$testcase]} != ${actual[$testcase]} ]; then
			failures=$(($failures+1))
		fi
	done
    correct=$((8-$failures))
	echo "$correct Correct  $failures Incorrect"
    exit $failures
}

runtests
showresults
