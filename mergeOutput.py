#!/usr/bin/env python3

import os
import argparse
import logging
import time
from ROOT import TFileMerger

class RootFileMerger:
    def __init__(self, base_dir, mergeFilePattern, output_file_name, logger=None):
        """
        Initialize:
         - base_dir: Base directory to search for files.
         - mergeFilePattern: Pattern used to match files (e.g., "out_*.root").
         - output_file_name: Name of the merged output file.
         - logger: Logger instance for logging messages.
        """
        self.base_dir = base_dir
        self.mergeFilePattern = mergeFilePattern
        self.output_file_name = output_file_name
        self.file_dict = {}   # Dictionary mapping directory to list of matching .root files
        self.all_files = []   # List of all matching files
        self.logger = logger if logger else logging.getLogger("merger")

    def log(self, message):
        self.logger.info(message)

    def gather_files(self):
        """
        Recursively search the base_dir for .root files that match the mergeFilePattern.
        Logs the number of matching files found in each subdirectory.
        """
        for root, dirs, files in os.walk(self.base_dir):
            matching_files = [os.path.join(root, f) for f in files
                              if f.lower().endswith('.root') and self.mergeFilePattern.split('*')[0].lower() in f.lower()]
            if matching_files:
                self.file_dict[root] = matching_files
                self.all_files.extend(matching_files)
                self.log(f"\n\n-------------------------------------------------------------------------\n")
                self.log(f"There are {len(matching_files)} .root files in directory '{root}'.")
                self.log(f"\n-------------------------------------------------------------------------\n\n")

    def estimate_total_size(self):
        """
        Estimate the total size (in bytes) of the collected files.
        Logs the size of each file and the overall estimated size.
        """
        total_size = 0
        for file_path in self.all_files:
            try:
                size = os.path.getsize(file_path)
                total_size += size
                self.log(f"The size of file '{file_path}' is {size/1024:.2f} KB.")
                self.log(f"The size of file '{file_path}' is {size/1024**3:.2f} GB.")
            except Exception as e:
                self.log(f"Failed to get size for file '{file_path}': {e}")

        self.log(f"\n\n-------------------------------------------------------------------------\n")
        self.log(f"Estimated total size before merging is {total_size/1024:.2f} KB.")
        self.log(f"Estimated total size before merging is {total_size/1024**3:.2f} GB.")
        self.log(f"\n-------------------------------------------------------------------------\n\n")

        return total_size

    def merge_files(self):
        """
        Merge all collected .root files into one output file using TFileMerger.
        Logs the progress of the merging process.
        """
        merger = TFileMerger(False)
        merger.SetPrintLevel(0)  # Suppress ROOT internal output
        merger.OutputFile(self.output_file_name)
        for file_path in self.all_files:
            merger.AddFile(file_path)
            self.log(f"Added file '{file_path}' to the merge list.")
        self.log("Starting the merge process.")
        success = merger.Merge()
        if not success:
            self.log("The merge process failed!")
            return False
        else:
            self.log("The merge process completed successfully.")
            return True

    def compare_sizes(self, estimated_size):
        """
        Compare the actual size of the merged file with the estimated size and log the difference.
        """

        self.log(f"\n\n-------------------------------------------------------------------------\n")

        try:
            final_size = os.path.getsize(self.output_file_name)
            self.log(f"The merged file '{self.output_file_name}' has a size of {final_size/1024:.2f} KB.")
            diff = final_size - estimated_size
            self.log(f"The difference between the estimated and merged file size is {diff/1024:.2f} KB.")
            return final_size
        except Exception as e:
            self.log(f"Failed to obtain the size of the merged file: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(
        description="ROOT file merger script",
        epilog="Example: python3 mergeOutput.py --dir /path/to/dir --pat out_*.root --out merged.root"
    )
    parser.add_argument("--dir", dest="base_dir", type=str, default=".", help="Base directory to search (default: current directory)")
    parser.add_argument("--pat", dest="mergeFilePattern", type=str, default="out_*.root", help="File pattern to match (default: out_*.root)")
    parser.add_argument("--out", dest="output_file_name", type=str, default="merged.root", help="Output merged file name (default: merged.root)")
    args = parser.parse_args()

    # Ensure base_dir is absolute.
    args.base_dir = os.path.abspath(args.base_dir)

    # Setup logger to output directly to console.
    logger = logging.getLogger("merger")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("  [ Merging log ]: %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    logger.info("Collecting .root files from subdirectories.")
    
    start_time = time.time()

    merger_instance = RootFileMerger(args.base_dir, args.mergeFilePattern, args.output_file_name, logger)
    merger_instance.gather_files()
    estimated_size = merger_instance.estimate_total_size()
    if merger_instance.merge_files():
        merger_instance.compare_sizes(estimated_size)
    else:
        logger.info("The overall merge process failed.")

    elapsed_time = time.time() - start_time  
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    logger.info(f"The merge job completed in {elapsed_time:.2f} seconds "
            f"({minutes} minutes and {seconds:.2f} seconds).")

    self.log(f"\n-------------------------------------------------------------------------\n\n")


if __name__ == "__main__":
    main()
