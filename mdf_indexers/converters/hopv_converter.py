import json
import sys
import os
from ..validator.schema_validator import Validator

# VERSION 0.2.0

# This is the converter for
# Arguments:
#   input_path (string): The file or directory where the data resides.
#       NOTE: Do not hard-code the path to the data in the converter. The converter should be portable.
#   metadata (string or dict): The path to the JSON dataset metadata file, a dict or json.dumps string containing the dataset metadata, or None to specify the metadata here. Default None.
#   verbose (bool): Should the script print status messages to standard output? Default False.
#       NOTE: The converter should have NO output if verbose is False, unless there is an error.
def convert(input_path, metadata=None, verbose=False):
    if verbose:
        print("Begin converting")

    # Collect the metadata
    if not metadata:
        dataset_metadata = {
            "mdf-title": "Harvard Organic Photovoltaic Dataset",
            "mdf-acl": ["public"],
            "mdf-source_name": "hopv",
            "mdf-citation": ["Aspuru-Guzik, Alan (2016): The Harvard Organic Photovoltaics 2015 (HOPV) dataset: An experiment-theory calibration resource.. Figshare. https://doi.org/10.6084/m9.figshare.1610063.v4"],
            "mdf-data_contact": {

                "given_name": "Alan",
                "family_name": "Aspuru-Guzik",

                "email": "alan@aspuru.com",
                "institution": "Harvard University"
                },

            "mdf-author": [{

                "given_name": "Alan",
                "family_name": "Aspuru-Guzik",

                "email": "alan@aspuru.com",
                "institution": "Harvard University"
                }],

            "mdf-license": "https://creativecommons.org/licenses/by/4.0/",

            "mdf-collection": "Harvard Organic Photovoltaic Dataset",
            "mdf-data_format": ["text"],
            "mdf-data_type": ["DFT", "experimental"],
            "mdf-tags": ["Organic Photovoltaic Cells", "quantum chemistry", "density functional theory", "calibration"],

            "mdf-description": "The Harvard Organic Photovoltaic Dataset (HOPV15) presented in this work is a collation of experimental photovoltaic data from the literature, and corresponding quantum-chemical calculations performed over a range of geometries, each with quantum chemical results using a variety of density functionals and basis sets.",
            "mdf-year": 2016,

            "mdf-links": {

                "mdf-landing_page": "https://figshare.com/articles/HOPV15_Dataset/1610063/4",

                "mdf-publication": ["https://dx.doi.org/10.1038/sdata.2016.86"],
                "mdf-dataset_doi": "https://dx.doi.org/10.6084/m9.figshare.1610063.v4"

#                "mdf-related_id": ,

                # data links: {

                    #"globus_endpoint": ,
                    #"http_host": ,

                    #"path": ,
                    #}
                },

#            "mdf-mrr": ,

            "mdf-data_contributor": [{

                "given_name": "Jonathon",
                "family_name": "Gaff",

                "email": "jgaff@uchicago.edu",
                "institution": "The University of Chicago",
                "github": "jgaff"
                }]
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


    dataset_validator = Validator(dataset_metadata)


    # Get the data
    with open(os.path.join(input_path, "HOPV_15_revised_2.data"), 'r') as in_file:
        index = 0
        eof = False
        smiles = in_file.readline() # Priming read
        if not smiles:
            eof = True
        while not eof:
            index += 1
            filename = "hopv_" + str(index) + ".txt"
            #Molecule level
            molecule = {}
            molecule["smiles"] = smiles.strip()
            molecule["inchi"] = in_file.readline().strip()
            exp_data = in_file.readline().strip().split(',')
            molecule["experimental_data"] = {
                "doi" : exp_data[0],
                "inchikey" : exp_data[1],
                "construction" : exp_data[2],
                "architecture" : exp_data[3],
                "complement" : exp_data[4],
                "homo" : float(exp_data[5]),
                "lumo" : float(exp_data[6]),
                "electrochemical_gap" : float(exp_data[7]),
                "optical_gap" : float(exp_data[8]),
                "pce" : float(exp_data[9]),
                "voc" : float(exp_data[10]),
                "jsc" : float(exp_data[11]),
                "fill_factor" : float(exp_data[12])
                }
            molecule["pruned_smiles"] = in_file.readline().strip()
            molecule["num_conformers"] = int(in_file.readline().strip())
            #Conformer level
            list_conformers = []
            for i in range(molecule["num_conformers"]):
                conformer = {}
                conformer["conformer_number"] = int(in_file.readline().strip("\n Cconformer"))
                conformer["num_atoms"] = int(in_file.readline().strip())
                #Atom level
                list_atoms = []
                for j in range(conformer["num_atoms"]):
                    atom_data = in_file.readline().strip().split(' ')
                    atom = {
                        "element" : atom_data[0],
                        "x_coordinate" : float(atom_data[1]),
                        "y_coordinate" : float(atom_data[2]),
                        "z_coordinate" : float(atom_data[3])
                        }
                    list_atoms.append(atom)
                conformer["atoms"] = list_atoms
                #Four sets of calculated data
                list_calc = []
                for k in range(4):
                    calc_data = in_file.readline().strip().split(",")
                    calculated = {
                        "set_description" : calc_data[0],
                        "homo" : float(calc_data[1]),
                        "lumo" : float(calc_data[2]),
                        "gap" : float(calc_data[3]),
                        "scharber_pce" : float(calc_data[4]),
                        "scharber_voc" : float(calc_data[5]),
                        "scharber_jsc" : float(calc_data[6])
                        }
                    list_calc.append(calculated)
                conformer["calculated_data"] = list_calc
                list_conformers.append(conformer)
            molecule["conformers"] = list_conformers

            uri = "/collections/hopv/" + filename

            record_metadata = {
                "mdf-title": "HOPV - " + molecule["smiles"],
                "mdf-acl": ["public"],

#                "mdf-tags": ,
#                "mdf-description": ,
                
                "mdf-composition": molecule["smiles"],
#                "mdf-raw": ,

                "mdf-links": {
#                    "mdf-landing_page": ,

#                    "mdf-publication": ,
#                    "mdf-dataset_doi": ,

#                    "mdf-related_id": ,

                     "molecule": {
     
                        "globus_endpoint": "82f1b5c6-6e9b-11e5-ba47-22000b92c6ec",
                        "http_host": "https://data.materialsdatafacility.org",

                        "path": uri
                        },
                    "original": {
                        "globus_endpoint": "82f1b5c6-6e9b-11e5-ba47-22000b92c6ec",
                        "http_host": "https://data.materialsdatafacility.org",

                        "path": "/collections/hopv/HOPV_15_revised_2.data"
                        }
                    }

#                "mdf-citation": ,
#                "mdf-data_contact": {

#                    "given_name": ,
#                    "family_name": ,

#                    "email": ,
#                    "institution":,

                    # IDs
#                },

#                "mdf-author": ,

#                "mdf-license": ,
#                "mdf-collection": ,
#                "mdf-data_format": ,
#                "mdf-data_type": ,
#                "mdf-year": ,

#                "mdf-mrr":

    #            "mdf-processing": ,
    #            "mdf-structure":,
                }

            # Pass each individual record to the Validator
            result = dataset_validator.write_record(record_metadata)

            # Check if the Validator accepted the record, and print a message if it didn't
            # If the Validator returns "success" == True, the record was written successfully
            if result["success"] is not True:
                print("Error:", result["message"])
                if verbose:
                    print(result["details"])
            else:
                with open(input_path + filename, 'w') as outfile:
                    json.dump(molecule, outfile)

            smiles = in_file.readline() # Next molecule
            if not smiles: # Empty line is EOF
                eof = True


    if verbose:
        print("Finished converting")