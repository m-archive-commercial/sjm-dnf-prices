"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 13:29
"""
import os.path

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.dirname(BASE_DIR)
PROJECT_DIR = os.path.dirname(SRC_DIR)
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")
OUT_DIR = os.path.join(PROJECT_DIR, "out")
