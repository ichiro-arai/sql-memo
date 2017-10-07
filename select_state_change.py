from datetime import date, timedelta
import random
import sqlite3

random.seed(0)

schema = """
CREATE TABLE IF NOT EXISTS logs (
  device_id TEXT,
  device_state TEXT,
  metrics DOUBLE,
  ts TIMESTAMP,
  PRIMARY KEY (device_id, ts)
)
"""

logging = """
INSERT INTO logs VALUES (?, ?, ?, ?)
"""

states = ['busy', 'idle', 'neko']

class Clock(object):
    dt = date(2000, 1, 1)

    def now(self):
        self.dt += timedelta(days=1)
        return self.dt


class Device(object):
    def __init__(self, name, clock):
        self.name = name
        self.clock = clock

    def log(self, con):
        i = random.randint(0, len(states) - 1)
        v = random.randint(0, 1000)
        con.execute(logging, (self.name, states[i], v, self.clock.now()))


clock = Clock()
devices = list(map(lambda name: Device(name, clock), ['p_0', 'T^1', 'L#2', 'B-3']))

con = sqlite3.connect(':memory:')
con.execute(schema)

# logging by each device
for t in range(20):
    i = random.randint(0, len(devices) - 1)
    devices[i].log(con)

# check
import sys
default_max_rows = int(sys.argv[1]) if len(sys.argv) > 2 else 6

def dump(title, statement, max_rows=default_max_rows):
    print('### ' + title)
    print('```sql')
    print(statement)
    print('```')
    try:
        import pandas as pd
        pd.set_option('display.width', 150)
        pd.set_option('display.max_rows', max_rows)
        result = pd.read_sql_query(statement, con)
    except ImportError:
        cursor = con.cursor()
        cursor.execute(statement)
        result = '\n'.join(map(lambda x: str(x), cursor.fetchall()))
        cursor.close()
    print('#### result:')
    print('\n```')
    print(result)
    print('```\n')

extract_state_change = """
SELECT
    subject.device_id,
    prev.device_id AS debug,
    prev.device_state AS prev_state,
    subject.device_state AS state,
    prev.metrics AS prev_value,
    subject.metrics AS value,
    prev.ts AS prev_ts,
    subject.ts AS ts
  FROM logs AS prev, logs AS subject
 WHERE prev.device_id = subject.device_id
   AND prev.ts = (
    SELECT MAX(precedings.ts) AS just_before FROM logs AS precedings
     WHERE precedings.ts < subject.ts
       AND precedings.device_id = subject.device_id
   )
""".strip()

# check base data
dump('check base data', 'SELECT * FROM logs', max_rows=6)
dump('check base data (sorted)', 'SELECT * FROM logs ORDER BY device_id, ts', max_rows=100)

# check with previous state
dump('check with previous state', extract_state_change)

# check if radical change
sql = extract_state_change + """
   AND prev_state = state
   AND subject.metrics - prev.metrics > 100
"""
dump('check if radical change', sql)

# select only state change
sql = extract_state_change + """
   AND subject.device_state <> prev.device_state"""
dump('select only state change', sql)


# filter if there may be logging failure in long time
sql = sql + """
   AND CAST(strftime('%s', subject.ts) as INT) - CAST(strftime('%s', prev.ts) as INT) < 60 * 60 * 24 * 3
"""
dump('filter if there may be logging failure in long time', sql)

con.close()
