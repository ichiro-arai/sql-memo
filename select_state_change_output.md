### check base data
```sql
SELECT * FROM logs
```
#### result:

```
   device_id device_state  metrics          ts
0        B-3         idle     41.0  2000-01-02
1        L#2         neko    497.0  2000-01-03
2        B-3         idle    991.0  2000-01-04
..       ...          ...      ...         ...
17       p_0         neko    505.0  2000-01-19
18       L#2         busy    747.0  2000-01-20
19       L#2         neko    891.0  2000-01-21

[20 rows x 4 columns]
```

### check base data (sorted)
```sql
SELECT * FROM logs ORDER BY device_id, ts
```
#### result:

```
   device_id device_state  metrics          ts
0        B-3         idle     41.0  2000-01-02
1        B-3         idle    991.0  2000-01-04
2        B-3         idle    597.0  2000-01-05
3        B-3         neko    103.0  2000-01-12
4        B-3         neko    266.0  2000-01-15
5        B-3         neko    844.0  2000-01-18
6        L#2         neko    497.0  2000-01-03
7        L#2         busy    773.0  2000-01-07
8        L#2         neko    722.0  2000-01-09
9        L#2         idle    323.0  2000-01-13
10       L#2         busy    747.0  2000-01-20
11       L#2         neko    891.0  2000-01-21
12       T^1         neko    142.0  2000-01-06
13       T^1         idle    101.0  2000-01-10
14       T^1         neko    488.0  2000-01-14
15       p_0         neko    818.0  2000-01-08
16       p_0         neko    338.0  2000-01-11
17       p_0         neko    937.0  2000-01-16
18       p_0         busy    736.0  2000-01-17
19       p_0         neko    505.0  2000-01-19
```

### check with previous state
```sql
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
```
#### result:

```
   device_id debug prev_state state  prev_value  value     prev_ts          ts
0        B-3   B-3       idle  idle        41.0  991.0  2000-01-02  2000-01-04
1        B-3   B-3       idle  idle       991.0  597.0  2000-01-04  2000-01-05
2        L#2   L#2       neko  busy       497.0  773.0  2000-01-03  2000-01-07
..       ...   ...        ...   ...         ...    ...         ...         ...
13       p_0   p_0       busy  neko       736.0  505.0  2000-01-17  2000-01-19
14       L#2   L#2       idle  busy       323.0  747.0  2000-01-13  2000-01-20
15       L#2   L#2       busy  neko       747.0  891.0  2000-01-20  2000-01-21

[16 rows x 8 columns]
```

### check if radical change
```sql
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
   AND prev_state = state
   AND subject.metrics - prev.metrics > 100

```
#### result:

```
  device_id debug prev_state state  prev_value  value     prev_ts          ts
0       B-3   B-3       idle  idle        41.0  991.0  2000-01-02  2000-01-04
1       B-3   B-3       neko  neko       103.0  266.0  2000-01-12  2000-01-15
2       p_0   p_0       neko  neko       338.0  937.0  2000-01-11  2000-01-16
3       B-3   B-3       neko  neko       266.0  844.0  2000-01-15  2000-01-18
```

### select only state change
```sql
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
   AND subject.device_state <> prev.device_state
```
#### result:

```
   device_id debug prev_state state  prev_value  value     prev_ts          ts
0        L#2   L#2       neko  busy       497.0  773.0  2000-01-03  2000-01-07
1        L#2   L#2       busy  neko       773.0  722.0  2000-01-07  2000-01-09
2        T^1   T^1       neko  idle       142.0  101.0  2000-01-06  2000-01-10
..       ...   ...        ...   ...         ...    ...         ...         ...
7        p_0   p_0       busy  neko       736.0  505.0  2000-01-17  2000-01-19
8        L#2   L#2       idle  busy       323.0  747.0  2000-01-13  2000-01-20
9        L#2   L#2       busy  neko       747.0  891.0  2000-01-20  2000-01-21

[10 rows x 8 columns]
```

### filter if there may be logging failure in long time
```sql
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
   AND subject.device_state <> prev.device_state
   AND CAST(strftime('%s', subject.ts) as INT) - CAST(strftime('%s', prev.ts) as INT) < 60 * 60 * 24 * 3

```
#### result:

```
  device_id debug prev_state state  prev_value  value     prev_ts          ts
0       L#2   L#2       busy  neko       773.0  722.0  2000-01-07  2000-01-09
1       p_0   p_0       neko  busy       937.0  736.0  2000-01-16  2000-01-17
2       p_0   p_0       busy  neko       736.0  505.0  2000-01-17  2000-01-19
3       L#2   L#2       busy  neko       747.0  891.0  2000-01-20  2000-01-21
```

