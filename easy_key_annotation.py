import argparse
import os
import pandas as pd
import json
import logging

VERSION = "0.1.0"
EXPECTED_KEYS_TABLE = ["file", "separator", "columns", "target_columns", "key_column", "annotation"]
EXPECTED_KEYS_LIST = ["file", "target_columns", "annotation"]

def merge_columns(df, target_column, columns_to_merge):
  """Merges multiple columns into a new column with distinct values separated by semi-colons.

  Args:
    df: The input DataFrame.
    columns_to_merge: A list of column names to merge.

  Returns:
    The DataFrame with the new "merged" column.
  """
  df[target_column] = df[columns_to_merge].apply(
      lambda row: ';'.join(sorted(set(str(x) for x in row.dropna() if x is not None))), axis=1
  )
  df.drop(columns=columns_to_merge, inplace=True)
  return df


def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Define arguments
    parser = argparse.ArgumentParser("Easy Key Annotation v{}".format(VERSION))
    parser.add_argument("--input", type=str, required=True, help="Path to the input file")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration JSON file")
    parser.add_argument("--key_column", type=str, required=True, help="Column name of the key column in the input file")
    parser.add_argument("--sep", type=str, required=False, help="Separator used in the input file", default="\t")
    args = parser.parse_args()

    input_file = args.input
    sep = args.sep
    key_column = args.key_column
    config_file = args.config
    output_file = args.output

    # Log arguments
    logger.info("Starting Easy Key Annotation v{}".format(VERSION))
    logger.info("Input file: {}".format(input_file))
    logger.info("Output file: {}".format(output_file))
    logger.info("Config file: {}".format(config_file))
    logger.info("Key column: {}".format(key_column))
    logger.info("Separator: {}".format(sep))
    logger.info("=====================================")

    # Read input files
    if not os.path.exists(input_file):
        logger.error(f"Input file {input_file} not found")
        exit(1)
    df = pd.read_csv(input_file, sep=sep)
    logging.info(f"Read {len(df)} rows from {input_file}")

    # Check if key column exists, raise error if not
    if key_column not in df.columns:
        logger.error(f"Key column {key_column} not found in input file")
        exit(1)

    # Read config file
    if not os.path.exists(config_file):
        logger.error(f"Config file {config_file} not found")
        exit(1)
    config = json.load(open(config_file))

    # set index to key column leaving it in the dataframe
    df.set_index(key_column, inplace=True, drop=False)

    # Perform sanity check on config file
    # Check that all table keys have an existing file, the expected keys and that the target columns, columns and annotation lists are the same length
    for k, dataset_config in config.items():
        if not os.path.exists(dataset_config["file"]):
            logger.error(f"File {dataset_config['file']} not found for dataset {k}")
            exit(1)
        if k == "table":
            expected_keys = EXPECTED_KEYS_TABLE
            if not len(dataset_config["columns"]) == len(dataset_config["target_columns"]) == len(dataset_config["annotation"]):
                logger.error(f"Columns, target_columns and annotation lists must be the same length for dataset {k}: {dataset_config['file']}")
                exit(1)
        else:
            expected_keys = EXPECTED_KEYS_LIST

        for key in expected_keys:
            if key not in dataset_config:
                logger.error(f"Expected {key} not found in dataset {k}: {dataset_config['file']}")
                exit(1)
        
    # Read annotation and merge them in df
    # Here we also keep track if a target column is present multiple times
    target_columns = {}
    col_idx = 0
    for k, dataset_config in config.items():
        col_idx += 1
        if k == "table":
            logger.info(f"Processing table dataset {dataset_config['file']}")
            annotation = pd.read_csv(dataset_config["file"], sep=dataset_config["separator"], index_col=dataset_config["key_column"])
            annotation = annotation[dataset_config["target_columns"]]
            col_names_dict = dict(zip(dataset_config["columns"], dataset_config["target_columns"]))
            annotation.rename(columns=col_names_dict, inplace=True)
            col_annotation_mode = dict(zip(dataset_config["target_columns"], dataset_config["annotation"]))
            for col, mode in col_labels_dict.items():
                if col not in target_columns: target_columns[col] = set()
                # Rename col in annotation to col_tmpmerge_idx 
                annotation.rename(columns={col: f"{col}_tmpmerge_{col_idx}"}, inplace=True)
                target_columns[col].add(f"{col}_tmpmerge_{col_idx}")
                if mode == "label": df = df.join(annotation[f"{col}_tmpmerge_{col_idx}"], how='left')
                if mode == "boolean": df[f"{col}_tmpmerge_{col_idx}"] = df[key_column].isin(annotation[col])
        else:
            logger.info(f"Processing gene list dataset {dataset_config['file']}")
            with open(dataset_config["file"]) as f:
                annotation = [x.strip() for x in f.readlines()]
            col_annotation_mode = dict(zip(dataset_config["target_columns"], dataset_config["annotation"]))
            for col, mode in col_labels_dict.items():
                target_columns[col].add(f"{col}_tmpmerge_{col_idx}")
                if mode == "label": df[f"{col}_tmpmerge_{col_idx}"] = df[key_column].apply(lambda i: x if i in annotation else None)
                if mode == "boolean": df[f"{col}_tmpmerge_{col_idx}"] = df[key_column].isin(annotation) 

    logger.info("Merging columns")
    for col, cols_to_merge in target_columns.items():
        df = merge_columns(df, target_column=col, cols_to_merge=cols_to_merge)

    logger.info(f"Final list of columns added: {list(my_dict.keys())}")

    # Write output file
    logger.info(f"Writing output file to {output_file}")
    df.to_csv(output_file, sep=sep, index=False)
    logger.info("Done")

if __name__ == "__main__":
    main()
