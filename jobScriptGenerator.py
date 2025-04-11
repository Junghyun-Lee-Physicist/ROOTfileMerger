#!/usr/bin/env python3

import os
import argparse

def generate_local_merge_script(storage_path, scriptForMerge, mergeFilePattern):
    """
    Generate a local run shell script that will run the merge script for every subdirectory under storage_path.
    Each job will merge the files within one subdirectory using the given output file pattern.
    """
    # List all subdirectories within storage_path.
    subdirs = [d for d in os.listdir(storage_path) if os.path.isdir(os.path.join(storage_path, d))]
    
    lines = [
        "#!/bin/bash",
        f'MERGE_DIR="{storage_path}"',
        'echo -e "  -- merger script -- > Set ntuple path [ ${MERGE_DIR} ]"',
        ""
    ]
    
    # Loop over each subdirectory found.
    for subdir in subdirs:
        lines.append(f'echo "Processing directory: {subdir}"')
        # Here, the command calls mergeOutput.py with:
        # --dir pointing to the subdirectory,
        # --pat using the mergeFilePattern,
        # --out naming the merged file as <subdir>.root within the storage path.
        lines.append(f'python3 -u mergeOutput.py --dir "${{MERGE_DIR}}/{subdir}" --pat {mergeFilePattern} --out "${{MERGE_DIR}}/{subdir}.root"')
        lines.append("")
    
    lines.append('echo "All merge jobs completed."')
    
    with open(scriptForMerge, "w") as f:
        f.write("\n".join(lines))
    os.chmod(scriptForMerge, 0o755)
    print(f"Local run script generated: {scriptForMerge}")

def generate_condorMerge_submission_file(storage_path, scriptForMerge, mergeFilePattern):
    """
    Generate a Condor job submission file. Each subdirectory under storage_path will be
    treated as an individual job that merges all files within that subdirectory.
    """
 
    lines = [
        "Executable      = mergeOutput.py",
        "getenv          = True",
        "should_transfer_files = No",
        '+JobFlavour      = "tomorrow"',
        ""
    ]
    
    # List all subdirectories within storage_path.
    subdirs = [d for d in os.listdir(storage_path) if os.path.isdir(os.path.join(storage_path, d))]
 
    # Create a directory for Condor logs if it doesn't exist
    merge_condor_logs_dir = "merge_condor_logs"
    os.makedirs(merge_condor_logs_dir, exist_ok=True)

    for subdir in subdirs:
        full_dir = os.path.join(storage_path, subdir)
        # Each job uses the full directory as parameter and names the merged file as <subdir>.root.
        lines.append(f'arguments = --dir {full_dir} --pat {mergeFilePattern} --out {full_dir}.root')
        lines.append(f"Output          = merge_condor_logs/{subdir}_$(Cluster)_$(Process).out")
        lines.append(f"Error           = merge_condor_logs/{subdir}_$(Cluster)_$(Process).err")
        lines.append(f"Log             = merge_condor_logs/{subdir}_$(Cluster).log")
        lines.append("queue")
        lines.append("")
    
    with open(scriptForMerge, "w") as f:
        f.write("\n".join(lines))
    print(f"Condor submission file generated: {scriptForMerge}")

def main():
    parser = argparse.ArgumentParser(
        description="Job Script Generator for the ROOT file merger",
        epilog="Generates either a local run script or a Condor job submission file based on all subdirectories under a given storage path."
    )
    parser.add_argument("--mode", type=str, choices=["local", "condor"], required=True,
                        help="Mode: 'local' for local run script, 'condor' for Condor submission file.")
    args = parser.parse_args()

    username = os.getenv("USER")
    storage_path = f"/eos/cms/store/group/phys_jetmet/{username}/JMETriggerAnalysis/JESC/JESC_ntuple/250407_winter25v9/"
    mergeFilePattern = "out_*.root"
    
    if args.mode == "local":
        scriptForMerge = "merge_Locally.sh"
        generate_local_merge_script(storage_path, scriptForMerge, mergeFilePattern)
    elif args.mode == "condor":
        scriptForMerge = "merge_using_condor.sub"
        generate_condorMerge_submission_file(storage_path, scriptForMerge, mergeFilePattern)

if __name__ == "__main__":
    main()
