from collections import namedtuple

# Conversion tasks list table columns
TableColumns = namedtuple("TableColumns", "NAME DURATION QUALITY PROGRESS")
COLUMNS = TableColumns(*range(4))
