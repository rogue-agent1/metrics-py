#!/usr/bin/env python3
"""Application metrics — counters, gauges, histograms, timers."""
import time, math, sys

class Counter:
    def __init__(self,name,help=""): self.name=name;self.help=help;self.value=0
    def inc(self,n=1): self.value+=n
    def __repr__(self): return f"counter({self.name}={self.value})"

class Gauge:
    def __init__(self,name): self.name=name;self.value=0
    def set(self,v): self.value=v
    def inc(self,n=1): self.value+=n
    def dec(self,n=1): self.value-=n

class Histogram:
    def __init__(self,name,buckets=None):
        self.name=name;self.values=[];self.buckets=buckets or [0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2.5,5,10]
    def observe(self,v): self.values.append(v)
    def percentile(self,p):
        if not self.values: return 0
        s=sorted(self.values); return s[int(len(s)*p/100)]
    def summary(self):
        if not self.values: return {}
        return {"count":len(self.values),"sum":sum(self.values),
                "avg":sum(self.values)/len(self.values),
                "p50":self.percentile(50),"p95":self.percentile(95),"p99":self.percentile(99)}

class Timer:
    def __init__(self,histogram): self.hist=histogram;self.start=None
    def __enter__(self): self.start=time.perf_counter(); return self
    def __exit__(self,*_): self.hist.observe(time.perf_counter()-self.start)

class Registry:
    def __init__(self): self.metrics={}
    def counter(self,name): m=Counter(name); self.metrics[name]=m; return m
    def gauge(self,name): m=Gauge(name); self.metrics[name]=m; return m
    def histogram(self,name): m=Histogram(name); self.metrics[name]=m; return m
    def report(self):
        for name,m in self.metrics.items():
            if isinstance(m,Counter): print(f"  {name}: {m.value}")
            elif isinstance(m,Gauge): print(f"  {name}: {m.value}")
            elif isinstance(m,Histogram): print(f"  {name}: {m.summary()}")

if __name__ == "__main__":
    reg=Registry()
    reqs=reg.counter("http_requests"); errors=reg.counter("http_errors")
    active=reg.gauge("active_connections"); latency=reg.histogram("request_latency")
    import random; random.seed(42)
    for _ in range(100):
        reqs.inc(); active.inc()
        with Timer(latency): time.sleep(random.uniform(0.0001,0.001))
        if random.random()<0.05: errors.inc()
        active.dec()
    reg.report()
