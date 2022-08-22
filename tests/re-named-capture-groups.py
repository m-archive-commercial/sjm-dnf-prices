"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 20, 2022, 19:18
"""
import re


print(re.search(r'age: (?P<age>\d+)', 'age: 17').group('age'))
