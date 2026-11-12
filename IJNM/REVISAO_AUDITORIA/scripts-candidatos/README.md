# Candidate script corrections — audit branch

Branch: `audit/candidate-script-corrections-v1`

These files are **candidate, non-validated copies**. The original experiment scripts on `main` were not changed. No experiment was executed and no result was regenerated.

## Candidate changes

- Test 1: corrects the `bwm-ng -u packtes` spelling to `packets` and creates the requested capture directory.
- Test 2: directs new captures and extracted CSVs to `data/audit-v1/`, preventing overwrite of historical files; updates the candidate plotter input/output paths.
- Test 3: removes the dangling `-b` option from the TCP iperf3 commands (the paper describes TCP flows without a target bitrate cap) and isolates new captures/CSVs/graphs under `audit-v1`.
- Test 4 latency: aligns the candidate input directory with the path written by the current run script and writes output to a separate audit directory.
- Test 4 throughput: creates a correctly named throughput plotter copy, because the original `plotter_fct.py` plots bwm-ng throughput and does not calculate FCT.

## Validation still required

1. Review the intended `bwm-ng` option against the installed version.
2. Confirm Test 2 and Test 3 input/output paths using actual historical captures.
3. Confirm the intended TCP window value and iperf3 behavior in Test 3.
4. Test the latency parser against the actual ping log format and determine whether `run3/` represents a separate historical dataset.
5. Derive FCT independently from verified iperf3 logs. The candidate throughput plotter is not an FCT calculation.
6. Run static syntax checks and controlled test runs in the documented Mininet/BMv2 environment.
7. Compare any new outputs with the publication without replacing published or original values.

Do not merge these candidates into `main` or use them to claim reproduction until all validation items are closed.
