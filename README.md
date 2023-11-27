# SlurmGen - Simple Slurm Manager

> * **Repository: [github.com/otvam/slurmgen](https://github.com/otvam/slurmgen)**
> * **Package: [pypi.org/project/slurmgen](https://pypi.org/project/slurmgen)**

## Summary

**SlurmGen** is a very **simple** **Slurm** manager:
* The job description is stored in a JSON file.
* The JSON file is transformed into a Slurm script.
* The Slurm file is submitted to the cluster.

**SlurmGen** is only supporting a small **subset** of **Slurm**:
* Create and delete folders.
* Set environment variables.
* Set the job name and log.
* Set the ressources (memory, time, CPU, etc.).
* Define the set of commands to be executed.

SlurmGen is not a binding and/or a wrapper for Slurm.
SlurmGen is only generating Slurm scripts from JSON files.

## Example

```bash
# Running this command will:
#   - Create a Slurm script "slurm_output/test.slm"
#   - Put the log file in "slurm_output/test.log"
#   - Run the Slurm script on the cluster
slurmgen test.json
```

## Project Links

* Repository: https://github.com/otvam/slurmgen
* Releases: https://github.com/otvam/slurmgen/releases
* Tags: https://github.com/otvam/slurmgen/tags
* Issues: https://github.com/otvam/slurmgen/issues
* PyPi: https://pypi.org/project/slurmgen

## Author

* **Thomas Guillod**
* Email: guillod@otvam.ch
* Website: https://otvam.ch

## Copyright

> (c) 2023 - Thomas Guillod - Dartmouth College
> 
>  BSD 2-Clause "Simplified" License
