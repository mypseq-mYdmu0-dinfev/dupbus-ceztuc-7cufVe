🛜 Ping Google:
ping -c 60 8.8.8.8
Sample Result:
--- 8.8.8.8 ping statistics ---
60 packets transmitted, 60 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 8.058/13.733/24.783/2.362ms

🗺️ Trace Route:
traceroute -m 20 8.8.8.8
Sample Result (Vocus):
traceroute to 8.8.8.8 (8.8.8.8), 20 hops max, 40 byte packets
 1  192.168.0.1 (192.168.0.1)  1.937 ms  2.482 ms  1.950 ms
 2  203-134-80-40.core.vocus.network (203.134.80.40)  11.007 ms  14.471 ms  14.892 ms
 3  * * *
 4  as15169.per03.sydnmtc.nsw.vocus.network (203.134.8.247)  15.044 ms  10.483 ms *
 5  * * *
...