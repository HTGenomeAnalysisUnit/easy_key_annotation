# Easy annotation by key

This is a simple annotation tool that allows to annotate a table using multiple sources defined in JSON configuration file.

Given an input file and a configure key column, various annotations can be added linked to the key column with configurable column names.

## Usage

```bash
usage: easy_key_annotation.py [-h] --input INPUT --output OUTPUT --config CONFIG --key_column KEY_COLUMN [--sep SEP]

Annotate a key column in a file with additional information from other files

options:
  -h, --help            show this help message and exit
  --input INPUT         Path to the input file
  --output OUTPUT       Path to the output file
  --config CONFIG       Path to the configuration JSON file
  --key_column KEY_COLUMN
                        Column name of the key column in the input file
  --sep SEP             Separator used in the input file
```

At the moment, it expects a table as input with one column representing the key column. Information from the configured sources will be merged into the table by joining on the key column. All files are expected to have an heder row.

When multiple sources are configured to annotated the same target column, the resulting annotation will be a semi-column separated list of distinct values across all these sources.

## Annotation sources

Annotation sources can either be tables or lists of IDs. 

- **Tables**: in this case you can configure which column from the annotation table to use as annotation and the corresponding column name in the output table. For each column you can defined if the annotation mode is `label`, then the corresponding value is annotated, or `boolean`, then we expect the column to contain a list of IDs that can be matched agains the input file key column and the annotation will be a 0/1 value (1 if the key is present in the list, 0 otherwise).
- **Gene lists**: in this case you can configure the column name(s) in the output table and the corresponding annotation mode. The file should contain a list of IDs that can be matched against the input file key column. In `boolean` mode the resulting column is a 0/1 value (1 if the key is present in the list, 0 otherwise), in `label` mode the resulting column will contain the label defined by `label` key in the configuration.

## Configuration

The configuration file is a JSON file that defines the sources to be used for annotation. Two types of sources are allowed: `tables` and `gene_lists`. In these categories you can provide a list of sources, each defined as a dictionary with the following keys. See also the `test.json` file in test folder for an example.

### Tables

```json
{
	"file": "annot_table1.tsv",
	"separator": "\t",
	"key_column": "id",
	"columns": ["col1", "col2"],
	"target_columns": ["col1_label", "is_in_col2"],
	"annotation": ["label", "boolean"]
}
```

- `file`: Path to the annotation table file
- `separator`: Separator used in the annotation table file
- `key_column`: Column name of the key column in the annotation table
- `columns`: List of relevant columns from the source
- `target_columns`: List of column names that will be added in the output table
- `annotation`: List of annotation modes for each column in `columns` (either `label` or `boolean`)

**NB:** The number of elements in `columns`, `target_columns`, and `annotation` should be the same.

### Gene lists

```json
{
  "file": "list2.txt",
  "label": "list2_label",
  "target_columns": ["gene_labels"],
  "annotation": ["label"]
}
```

- `file`: Path to the annotation table file
- `label`: A label to be used as annotation in the output table (this is mandatory even if the annotation mode is `boolean`)
- `target_columns`: List of column names that will be added in the output table
- `annotation`: List of annotation modes for each column in `columns` (either `label` or `boolean`)

**NB:** The number of elements in `target_columns` and `annotation` should be the same.
