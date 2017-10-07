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
```
#### result:

```
   device_id debug state prev_state  value  prev_value          ts     prev_ts   diff  interval
0        B-3   B-3  idle       idle  991.0        41.0  2000-01-04  2000-01-02  950.0    172800
1        B-3   B-3  idle       idle  597.0       991.0  2000-01-05  2000-01-04 -394.0     86400
2        L#2   L#2  busy       neko  773.0       497.0  2000-01-07  2000-01-03  276.0    345600
..       ...   ...   ...        ...    ...         ...         ...         ...    ...       ...
13       p_0   p_0  neko       busy  505.0       736.0  2000-01-19  2000-01-17 -231.0    172800
14       L#2   L#2  busy       idle  747.0       323.0  2000-01-20  2000-01-13  424.0    604800
15       L#2   L#2  neko       busy  891.0       747.0  2000-01-21  2000-01-20  144.0     86400

[16 rows x 10 columns]
```

### check if radical change
```sql
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
   AND prev_state = state
   AND (diff > 100 OR diff < -100)

```
#### result:

```
  device_id debug state prev_state  value  prev_value          ts     prev_ts   diff  interval
0       B-3   B-3  idle       idle  991.0        41.0  2000-01-04  2000-01-02  950.0    172800
1       B-3   B-3  idle       idle  597.0       991.0  2000-01-05  2000-01-04 -394.0     86400
2       p_0   p_0  neko       neko  338.0       818.0  2000-01-11  2000-01-08 -480.0    259200
3       B-3   B-3  neko       neko  266.0       103.0  2000-01-15  2000-01-12  163.0    259200
4       p_0   p_0  neko       neko  937.0       338.0  2000-01-16  2000-01-11  599.0    432000
5       B-3   B-3  neko       neko  844.0       266.0  2000-01-18  2000-01-15  578.0    259200
```

### select only state change
```sql
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
   AND t1.device_state <> t2.device_state

```
#### result:

```
   device_id debug state prev_state  value  prev_value          ts     prev_ts   diff  interval
0        L#2   L#2  busy       neko  773.0       497.0  2000-01-07  2000-01-03  276.0    345600
1        L#2   L#2  neko       busy  722.0       773.0  2000-01-09  2000-01-07  -51.0    172800
2        T^1   T^1  idle       neko  101.0       142.0  2000-01-10  2000-01-06  -41.0    345600
..       ...   ...   ...        ...    ...         ...         ...         ...    ...       ...
7        p_0   p_0  neko       busy  505.0       736.0  2000-01-19  2000-01-17 -231.0    172800
8        L#2   L#2  busy       idle  747.0       323.0  2000-01-20  2000-01-13  424.0    604800
9        L#2   L#2  neko       busy  891.0       747.0  2000-01-21  2000-01-20  144.0     86400

[10 rows x 10 columns]
```

### filter if there may be logging failure in long time
```sql
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
   AND t1.device_state <> t2.device_state
   AND interval < 60 * 60 * 24 * 3
```
#### result:

```
  device_id debug state prev_state  value  prev_value          ts     prev_ts   diff  interval
0       L#2   L#2  neko       busy  722.0       773.0  2000-01-09  2000-01-07  -51.0    172800
1       p_0   p_0  busy       neko  736.0       937.0  2000-01-17  2000-01-16 -201.0     86400
2       p_0   p_0  neko       busy  505.0       736.0  2000-01-19  2000-01-17 -231.0    172800
3       L#2   L#2  neko       busy  891.0       747.0  2000-01-21  2000-01-20  144.0     86400
```

