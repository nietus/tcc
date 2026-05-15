# Drone routing experiments

This folder contains the first reproducible harness for the TCC problem:
multi-period drone routing with time windows and recharging stations.

Run the default representative experiment:

```powershell
python experiments\drone_routing.py
```

The script reads the Schneider/Goeke E-VRPTW instances from:

```text
data/raw/evrptw/instances/evrptw_instances
```

and writes CSV outputs to:

```text
results/drone_routing_full_small
```

Useful variants:

```powershell
python experiments\drone_routing.py --limit 36 --range-limit 60 --results-dir results\drone_routing_r60_full_small
python experiments\drone_routing.py --limit 36 --range-limit 100 --results-dir results\drone_routing_r100_full_small
python experiments\drone_routing.py --limit 36 --grasp-restarts 8 --vns-iterations 60
```

The current algorithms are `edd`, `sweep`, `nearest`, `grasp`, and `mp_eavns`. Station policies are `depot`, `phased`, and `all`.

Generate the first plots from the CSV outputs:

```powershell
python experiments\plot_results.py --results-dir results\drone_routing_full_small --figures-dir figures\drone_routing_full_small
```

The plotting script writes PNG files to:

```text
figures/drone_routing_full_small
```
