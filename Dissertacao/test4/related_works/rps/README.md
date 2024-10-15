# File organization

- \<fct_test> - directory where the data acquired in the FCT experiment is stored
- \<latency_testt> - directory where the data acquired in the latency experiment is stored
- \<p4src> directory where the configuration files for the experiment are stored

## Initial execution
1. Run the test:
```sh
$ sudo python3 run_test.py
```
2. Generate an FCT graph from the collected data:
```sh
$ sudo python3 plotter_fct.py
```
3. Generate a latency graph from the collected data:
```sh
$ sudo python3 plotter_latency.py
```
