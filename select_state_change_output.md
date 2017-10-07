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
3        B-3         idle    597.0  2000-01-05
4        T^1         neko    142.0  2000-01-06
5        L#2         busy    773.0  2000-01-07
6        p_0         neko    818.0  2000-01-08
7        L#2         neko    722.0  2000-01-09
8        T^1         idle    101.0  2000-01-10
9        p_0         neko    338.0  2000-01-11
10       B-3         neko    103.0  2000-01-12
11       L#2         idle    323.0  2000-01-13
12       T^1         neko    488.0  2000-01-14
13       B-3         neko    266.0  2000-01-15
14       p_0         neko    937.0  2000-01-16
15       p_0         busy    736.0  2000-01-17
16       B-3         neko    844.0  2000-01-18
17       p_0         neko    505.0  2000-01-19
18       L#2         busy    747.0  2000-01-20
19       L#2         neko    891.0  2000-01-21
20       p_0         busy    939.0  2000-01-22
21       T^1         busy    822.0  2000-01-23
22       T^1         neko    458.0  2000-01-24
23       p_0         busy    327.0  2000-01-25
24       B-3         busy    308.0  2000-01-26
25       L#2         neko    127.0  2000-01-27
26       L#2         neko    208.0  2000-01-28
27       L#2         idle     93.0  2000-01-29
28       B-3         idle    589.0  2000-01-30
29       T^1         idle    188.0  2000-01-31
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
3        L#2   L#2  neko       busy  722.0       773.0  2000-01-09  2000-01-07  -51.0    172800
4        T^1   T^1  idle       neko  101.0       142.0  2000-01-10  2000-01-06  -41.0    345600
5        p_0   p_0  neko       neko  338.0       818.0  2000-01-11  2000-01-08 -480.0    259200
6        B-3   B-3  neko       idle  103.0       597.0  2000-01-12  2000-01-05 -494.0    604800
7        L#2   L#2  idle       neko  323.0       722.0  2000-01-13  2000-01-09 -399.0    345600
8        T^1   T^1  neko       idle  488.0       101.0  2000-01-14  2000-01-10  387.0    345600
9        B-3   B-3  neko       neko  266.0       103.0  2000-01-15  2000-01-12  163.0    259200
10       p_0   p_0  neko       neko  937.0       338.0  2000-01-16  2000-01-11  599.0    432000
11       p_0   p_0  busy       neko  736.0       937.0  2000-01-17  2000-01-16 -201.0     86400
12       B-3   B-3  neko       neko  844.0       266.0  2000-01-18  2000-01-15  578.0    259200
13       p_0   p_0  neko       busy  505.0       736.0  2000-01-19  2000-01-17 -231.0    172800
14       L#2   L#2  busy       idle  747.0       323.0  2000-01-20  2000-01-13  424.0    604800
15       L#2   L#2  neko       busy  891.0       747.0  2000-01-21  2000-01-20  144.0     86400
16       p_0   p_0  busy       neko  939.0       505.0  2000-01-22  2000-01-19  434.0    259200
17       T^1   T^1  busy       neko  822.0       488.0  2000-01-23  2000-01-14  334.0    777600
18       T^1   T^1  neko       busy  458.0       822.0  2000-01-24  2000-01-23 -364.0     86400
19       p_0   p_0  busy       busy  327.0       939.0  2000-01-25  2000-01-22 -612.0    259200
20       B-3   B-3  busy       neko  308.0       844.0  2000-01-26  2000-01-18 -536.0    691200
21       L#2   L#2  neko       neko  127.0       891.0  2000-01-27  2000-01-21 -764.0    518400
22       L#2   L#2  neko       neko  208.0       127.0  2000-01-28  2000-01-27   81.0     86400
23       L#2   L#2  idle       neko   93.0       208.0  2000-01-29  2000-01-28 -115.0     86400
24       B-3   B-3  idle       busy  589.0       308.0  2000-01-30  2000-01-26  281.0    345600
25       T^1   T^1  idle       neko  188.0       458.0  2000-01-31  2000-01-24 -270.0    604800
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
6       p_0   p_0  busy       busy  327.0       939.0  2000-01-25  2000-01-22 -612.0    259200
7       L#2   L#2  neko       neko  127.0       891.0  2000-01-27  2000-01-21 -764.0    518400
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
3        B-3   B-3  neko       idle  103.0       597.0  2000-01-12  2000-01-05 -494.0    604800
4        L#2   L#2  idle       neko  323.0       722.0  2000-01-13  2000-01-09 -399.0    345600
5        T^1   T^1  neko       idle  488.0       101.0  2000-01-14  2000-01-10  387.0    345600
6        p_0   p_0  busy       neko  736.0       937.0  2000-01-17  2000-01-16 -201.0     86400
7        p_0   p_0  neko       busy  505.0       736.0  2000-01-19  2000-01-17 -231.0    172800
8        L#2   L#2  busy       idle  747.0       323.0  2000-01-20  2000-01-13  424.0    604800
9        L#2   L#2  neko       busy  891.0       747.0  2000-01-21  2000-01-20  144.0     86400
10       p_0   p_0  busy       neko  939.0       505.0  2000-01-22  2000-01-19  434.0    259200
11       T^1   T^1  busy       neko  822.0       488.0  2000-01-23  2000-01-14  334.0    777600
12       T^1   T^1  neko       busy  458.0       822.0  2000-01-24  2000-01-23 -364.0     86400
13       B-3   B-3  busy       neko  308.0       844.0  2000-01-26  2000-01-18 -536.0    691200
14       L#2   L#2  idle       neko   93.0       208.0  2000-01-29  2000-01-28 -115.0     86400
15       B-3   B-3  idle       busy  589.0       308.0  2000-01-30  2000-01-26  281.0    345600
16       T^1   T^1  idle       neko  188.0       458.0  2000-01-31  2000-01-24 -270.0    604800
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
4       T^1   T^1  neko       busy  458.0       822.0  2000-01-24  2000-01-23 -364.0     86400
5       L#2   L#2  idle       neko   93.0       208.0  2000-01-29  2000-01-28 -115.0     86400
```

