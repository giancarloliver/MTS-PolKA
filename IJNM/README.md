# IJNM experimental artifacts — MTS-PolKA

This directory contains the experiment material associated with the article *MTS-PolKA: Weighted Multipath Traffic Splitting With Source Routing for Elephant and Mice Flows*.

The repository files are retained as research artifacts. The descriptions below identify the organization found in the repository; they do not certify that every script can currently be rerun or that every stored output reproduces the published figures.

## Directory organization

```text
IJNM/
├── IJNM_MTS_Polka.pdf
├── README.md
├── scenario/
├── test1/
│   ├── conf/
│   ├── data/
│   ├── result/
│   ├── README.md
│   └── run_test1.py
├── test2/
│   ├── conf/
│   ├── data/
│   ├── result/
│   ├── README.md
│   ├── run_test-2.py
│   └── plotter_test-2.py
├── test3/
│   ├── conf/
│   ├── data/
│   ├── result/
│   ├── README.md
│   ├── run_test-3.py
│   └── grafico-test-3.py
└── test4/
    ├── scenario/
    ├── mts-polka/
    │   ├── conf_profile/
    │   ├── fct_test/
    │   ├── latency_test/
    │   ├── retransmission/
    │   ├── README.md
    │   ├── run_test-4.py
    │   ├── plotter_fct.py
    │   ├── plotter_latency.py
    │   └── plotter_retransmission.py
    └── related_works/
        ├── ecmp/
        ├── wcmp/
        └── rps/
```

The `m-polka/` implementation and configuration directory referenced by the experiment scripts is located outside `IJNM/`, at the repository root.

## Experiments

| Directory | Purpose indicated by the experiment artifacts | Main execution script | Analysis script |
|---|---|---|---|
| `test1/` | UDP traffic distribution under the configured traffic profiles | `run_test1.py` | Results and graphs in `result/` |
| `test2/` | Throughput behavior during profile changes | `run_test-2.py` | `plotter_test-2.py` |
| `test3/` | Concurrent TCP/UDP flows and profile/path reconfiguration | `run_test-3.py` | `grafico-test-3.py` |
| `test4/mts-polka/` | FCT, latency and TCP retransmission measurements for MTS-PolKA | `run_test-4.py` | `plotter_fct.py`, `plotter_latency.py`, `plotter_retransmission.py` |

The `test4/related_works/` subdirectories contain the corresponding experiment material for ECMP, WCMP and RPS. They are comparison artifacts and should be treated separately from the MTS-PolKA implementation.

## Execution references

The commands below identify the script names currently present in the repository. Execute them only in the experiment environment and after checking the required dependencies, paths and output directories.

```sh
cd IJNM/test1
sudo python3 run_test1.py

cd ../test2
sudo python3 run_test-2.py
python3 plotter_test-2.py

cd ../test3
sudo python3 run_test-3.py
python3 grafico-test-3.py

cd ../test4/mts-polka
sudo python3 run_test-4.py
python3 plotter_fct.py
python3 plotter_latency.py
python3 plotter_retransmission.py
```

## Audit notes — items not yet reconciled

The repository contains documentation/script inconsistencies that must be resolved before treating these commands as a reproducible procedure:

1. The previous root README repeated `test2/` as the directory for Experiment 3 and did not describe Experiment 4. This file corrects that top-level description.
2. `test2/run_test-2.py` writes the monitor capture under `data/run2/`, while its subsequent extraction commands read from `data/run/`. The plotter also reads from `data/run/`. This path mismatch remains pending correction in a separately versioned script.
3. `test2/README.md` refers to `plotter-test-2.py`; the script present in the repository is `plotter_test-2.py`.
4. `test3/run_test-3.py` contains TCP client commands with `-b` followed by `-w`, without an explicit bandwidth value for `-b`. The intended iperf3 parameters must be established before correction.
5. `test4/mts-polka/README.md` refers to `run_test.py`; the execution script present in the directory is `run_test-4.py`. The README also spells the latency directory as `latency_testt`, whereas the execution script writes to `latency_test/`.
6. In Test 4, the execution script writes ping logs to `latency_test/data/run/`, while `plotter_latency.py` currently reads from `latency_test/data/run3/`.
7. Test 1's monitor command contains the unit string `packtes`; verify the accepted `bwm-ng` unit option before producing any new capture.

These are audit findings, not authorization to overwrite historical files. Original captures, logs, CSVs, figures and published values must remain unchanged. Any corrected script or reprocessed output must be stored separately and linked to its source artifact in the pending-items matrix.

## Evidence and versioning policy

- Treat the article and its published appendix/figures as the published-result reference.
- Treat repository scripts, configurations, raw logs and CSVs as implementation/execution evidence, not as interchangeable sources.
- Do not replace a published value with a newly calculated value without recording the input files, parser/calculation method, script version and output.
- Preserve original files. Place corrected scripts and derived results in clearly named, versioned locations and record hashes/commit identifiers.
- The audit matrix is maintained at `REVISAO_AUDITORIA/MATRIZ_PENDENCIAS_POR_ARQUIVO.md`.
