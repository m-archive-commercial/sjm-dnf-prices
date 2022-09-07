"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 13:22
"""
import os
from datetime import datetime

from log import get_logger

logger = get_logger("utils-general")


def getCurTime():
    return datetime.now().strftime('%m-%dT%H:%M:%S')


def packOut(out_dir):
    fpOut = f'{out_dir}.zip'
    ZIP_COMMAND = f"zip {fpOut}  -r {out_dir}"
    os.system(ZIP_COMMAND)
    logger.info(f'packed output into file://{fpOut}')
