"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 20, 2022, 18:38
"""

import re

i = 1
test_str = 'age: 17, name: mark'
print('to test: ', test_str)
print('===')


def testCase(tester):
    global i
    print(f'[#{i}] tester: ', tester)
    s = re.sub(tester, funcNonCapture, test_str)
    print('output: ', s)
    print('---')
    i += 1


def funcNonCapture(m: re.Match):
    print('matched: ', m)
    print('group: ', m.group())
    print('groups: ', m.groups())
    return 'TRANSFORMED'


testCase(r'age: \d+')
testCase(r'age: (\d+)')
testCase(r'(?:age: )\d+')
testCase(r'(?:age: )(\d+)')
testCase(r'(?<=age: )\d+')
testCase(r'(?<=age: )(\d+)')
