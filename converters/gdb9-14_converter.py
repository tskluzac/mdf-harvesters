import json
import sys
import os
from tqdm import tqdm
from parsers.utils import find_files
from parsers.pymatgen_parser import parse_pymatgen
from validator import Validator

# VERSION 0.1.0

# This is the gdb9-14 dataset of the Quantum chemistry structures and properties of 134 kilo molecules
# Arguments:
#   input_path (string): The file or directory where the data resides. This should not be hard-coded in the function, for portability.
#   metadata (string or dict): The path to the JSON dataset metadata file, a dict or json.dumps string containing the dataset metadata, or None to specify the metadata here. Default None.
#   verbose (bool): Should the script print status messages to standard output? Default False.
#       NOTE: The converter should have NO output if verbose is False, unless there is an error.
def convert(input_path, metadata=None, verbose=False):
    if verbose:
        print("Begin converting")

    # Collect the metadata
    if not metadata:
        dataset_metadata = {
            "globus_subject": "http://qmml.org/datasets.html#gdb9-14",
            "acl": ["public"],
            "mdf_source_name": "gdb9-14",
            "mdf-publish.publication.collection": "gdb9-14",
#            "mdf_data_class": ,

            "cite_as": ["Raghunathan Ramakrishnan, Pavlo Dral, Matthias Rupp, O. Anatole von Lilienfeld: Quantum Chemistry Structures and Properties of 134 kilo Molecules, Scientific Data 1: 140022, 2014."],
            "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "mdf_version": "0.1.0",

            "dc.title": "Quantum Chemistry Structures and Properties of 134 kilo Molecules",
            "dc.creator": "Ramakrishnan, R., Dral, P. O., Rupp, M. & von lilienfeld, O. A",
            "dc.identifier": "http://qmml.org/datasets.html#gdb9-14",
            "dc.contributor.author": ["Raghunathan Ramakrishnan", "Pavlo Dral", "Matthias Rupp", "O. Anatole von Lilienfeld"],
            "dc.subject": ["Computational chemistry", "Density functional theory", "Quantum chemistry"],
            "dc.description": "133,885 small organic molecules with up to 9 C, O, N, F atoms, saturated with H. Geometries, harmonic frequencies, dipole moments, polarizabilities, energies, enthalpies, and free energies of atomization at the DFT/B3LYP/6-31G(2df,p) level of theory. For a subset of 6,095 constitutional isomers of C7H10O2, energies, enthalpies, and free energies of atomization are provided at the G4MP2 level of theory.",
            "dc.relatedidentifier": ["http://dx.doi.org/10.1038/sdata.2014.22"],
            "dc.year": 2014
            }
    elif type(metadata) is str:
        try:
            dataset_metadata = json.loads(metadata)
        except Exception:
            try:
                with open(metadata, 'r') as metadata_file:
                    dataset_metadata = json.load(metadata_file)
            except Exception as e:
                sys.exit("Error: Unable to read metadata: " + repr(e))
    elif type(metadata) is dict:
        dataset_metadata = metadata
    else:
        sys.exit("Error: Invalid metadata parameter")



    # Make a Validator to help write the feedstock
    # You must pass the metadata to the constructor
    # Each Validator instance can only be used for a single dataset
    #dataset_validator = Validator(dataset_metadata, strict=False)
    # You can also force the Validator to treat warnings as errors with strict=True
    dataset_validator = Validator(dataset_metadata, strict=True)


    # Get the data
    #    Each record should be exactly one dictionary
    #    It is recommended that you convert your records one at a time, but it is possible to put them all into one big list (see below)
    #    It is also recommended that you use a parser to help with this process if one is available for your datatype

    # Each record also needs its own metadata
    for data_file in tqdm(find_files(input_path, "xyz"), desc="Processing files", disable=not verbose):
        record = parse_pymatgen(os.path.join(data_file["path"], data_file["filename"]))
        if record["structure"]:
            comp = record["structure"]["material_composition"]
        elif record["molecule"]:
            comp = record["molecule"]["material_composition"]
        uri = "https://data.materialsdatafacility.org/collections/" + "gdb9-14/" + data_file["no_root_path"] + "/" + data_file["filename"]
        index = ""
        if data_file["no_root_path"] == "dsgdb9nsd.xyz":
            start = data_file["filename"].find('_')
            index = int(data_file["filename"][start+1:-4])
        record_metadata = {
            "globus_subject": uri,
            "acl": ["public"],
#            "mdf-publish.publication.collection": ,
#            "mdf_data_class": ,
            "mdf-base.material_composition": comp,

#            "cite_as": ,
#            "license": ,

            "dc.title": "gdb9-14 - " + data_file["filename"],
#            "dc.creator": ,
            "dc.identifier": uri,
#            "dc.contributor.author": ,
#            "dc.subject": ,
#            "dc.description": ,
#            "dc.relatedidentifier": ,
#            "dc.year": ,

            "data": {
#                "raw": ,
#                "files": ,
                "index": index
                }
            }

        # Pass each individual record to the Validator
        result = dataset_validator.write_record(record_metadata)

        # Check if the Validator accepted the record, and print a message if it didn't
        # If the Validator returns "success" == True, the record was written successfully
        if result["success"] is not True:
            print("Error:", result["message"], ":", result.get("invalid_metadata", ""))
        # The Validator may return warnings if strict=False, which should be noted
        if result.get("warnings", None):
            print("Warnings:", result["warnings"])

    # Alternatively, if the only way you can process your data is in one large list, you can pass the list to the Validator
    # You still must add the required metadata to your records
    # It is recommended to use the previous method if possible
    # result = dataset_validator.write_dataset(your_records_with_metadata)
    #if result["success"] is not True:
        #print("Error:", result["message"])

    # You're done!
    if verbose:
        print("Finished converting")


# Optionally, you can have a default call here for testing
# The convert function may not be called in this way, so code here is primarily for testing
if __name__ == "__main__":
    import paths
    convert(paths.datasets + "gdb9-14", verbose=True)
