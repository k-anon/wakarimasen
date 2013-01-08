#!/usr/bin/env python

import sys
sys.path.append('../')
import config

from migrate.versioning.shell import main

if __name__ == '__main__':
    main(debug='False', url=config.SQL_ENGINE, repository='./')
