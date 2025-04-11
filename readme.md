
# ROOTfileMerger

`ROOT File Merger and Job Script Generator`

This repository provides a set of Python tools designed to automate the merging of ROOT files and to generate job submission scripts for both local execution and HTCondor batch processing. The tools are intended to make your workflow more flexible and help you manage large numbers of ROOT files more efficiently.

----------

## Contents
- mergeOutput.py
A script that recursively searches for `.root` files matching a specified pattern under a given directory, merges them into a single output file using ROOT's `TFileMerger` utility, and logs the entire process including a measure of the time taken.

- jobScriptGenerator.py
A script that automatically generates job submission scripts. It examines the specified storage directory for subdirectories and creates:
  - A local run shell script that executes the merge operation for every subdirectory.
  - A Condor submission file where each subdirectory is treated as an independent job.
Only the mode (local or condor) is supplied as a command-line argument; all other parameters (like storage path, file pattern, etc.) are defined directly in the script for ease of customization.

----------

## Script Descriptions

### mergeOutput.py

- Overview
  - Purpose:
  Merge multiple ROOT files into one consolidated file.
  - Features:
    - Recursively searches the given base directory for ROOT files matching a defined pattern (default: out_*.root).
    - Logs information about the number of files found, each file’s size, the estimated total size, and details of the merging process.
    - Measures and reports the time taken to complete the merge.

    - Usage Example:
    ```bash
    python3 mergeOutput.py --dir /path/to/your/ntuple_directory --pat out_*.root --out merged.root
    ```

- Key Points
  - Logging:
  Uses the Python logging module for real-time console output. When invoked with python3 -u, the output is unbuffered.
  - Timing:
  The script records the start time before commencing and calculates the elapsed time after the merge process ends. Both the total elapsed time (in seconds) and its equivalent in minutes and seconds are logged.

### jobScriptGenerator.py

- Overview
  - Purpose:
  Generate job submission scripts for merging operations based on the subdirectories present in a specified storage path.
  - Features:
    - Local Mode:
    Creates a shell script (local_run.sh) that loops through each subdirectory under the storage path and calls mergeOutput.py with the appropriate parameters.
    - Condor Mode:
    Generates a Condor submission file (condor_job.sub) where each job is set up for a subdirectory. This file includes the necessary Condor directives (e.g., Executable, Output, Error, Log) and configures the job's arguments accordingly.
    - Usage Examples:
    For a local run script:
    ```bash
    python3 jobScriptGenerator.py --mode local
    ```

    For a Condor submission file:
    ```bash
    python3 jobScriptGenerator.py --mode condor
    ```

----------

## Setup and Execution
  1. Merge Locally:
  ```bash
  ./merge_Locally.sh
  ```

  2. Submit Condor Jobs:
  ```bash
  condor_submit merge_using_condor.sub
  ```

----------

## Summary

This repository offers a flexible solution for merging ROOT files and generating submission scripts suitable for both local and HTCondor environments. Modify the hardcoded variables as necessary to tailor the scripts to your particular dataset and workflow.
