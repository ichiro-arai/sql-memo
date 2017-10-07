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
for t in range(30):
    i = random.randint(0, len(devices) - 1)
    devices[i].log(con)

# check
def dump(title, statement):
    print('### ' + title)
    print('```sql')
    print(statement)
    print('```')
    try:
        import pandas as pd
        pd.set_option('display.width', 150)
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
    t1.device_id,
    t2.device_id AS debug,
    t1.device_state AS state,
    t2.device_state AS prev_state,
    t1.metrics AS value,
    t2.metrics AS prev_value,
    t1.ts AS ts,
    t2.ts AS prev_ts,
    t1.metrics - t2.metrics AS diff,
    CAST(strftime('%s', t1.ts) as integer) - CAST(strftime('%s', t2.ts) as integer) AS interval
  FROM logs AS t1, logs AS t2
 WHERE t1.device_id = t2.device_id
   AND t2.ts = (
    SELECT MAX(t3.ts) FROM logs AS t3
     WHERE t3.ts < t1.ts
       AND t3.device_id = t1.device_id
   )
""".strip()

# check base data
dump('check base data', 'SELECT * FROM logs')

# check with previous state
dump('check with previous state', extract_state_change)

# check if radical change
sql = extract_state_change + """
   AND prev_state = state
   AND (diff > 100 OR diff < -100)
"""
dump('check if radical change', sql)

# select only state change
sql = extract_state_change + """
   AND t1.device_state <> t2.device_state
"""
dump('select only state change', sql)


# filter if there may be logging failure in long time
dump('filter if there may be logging failure in long time', sql + "   AND interval < 60 * 60 * 24 * 3")

con.close()
