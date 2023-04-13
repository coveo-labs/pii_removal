# Remove PII data

Python Pipeline Extension script.

Using a bunch of regex clean the metadata + file contents from PII data.

PII data is replaced with for example `[EMAIL]`.

## Inputs/configuration

| name                    | description                                                                   | example                                 |
| ----------------------- | ----------------------------------------------------------------------------- | --------------------------------------- |
| list_of_fields_to_check | List of the metadata names to check. Leave empty to check all fields          | ["author","subject","message"]          |
| use_original_file       | Do you want to load the original file contents (use in Pre-conversion script) | True                                    |
| badWords                | List of badwords to remove from the contents                                  | ["xxx","example.com"]                   |
| log_field               | Metadata field to use for logging the pii report                              | "log_pii" Make sure to create the field |
| test                    | If you want to test it locally                                                | False                                   |
