import json
import sys
from validator import Validator
import xlrd


# This is the template for new converters. It is not a complete converter. Incomplete parts are labelled with "TODO"
# Arguments:
#   input_path (string): The file or directory where the data resides. This should not be hard-coded in the function, for portability.
#   metadata (string or dict): The path to the JSON dataset metadata file, a dict containing the dataset metadata, or None to specify the metadata here. Default None.
#   verbose (bool): Should the script print status messages to standard output? Default False.
def convert(input_path, metadata=None, verbose=False):
    if verbose:
        print("Begin converting")

    # Collect the metadata
    # Fields can be:
    #    REQ (Required, must be present)
    #    RCM (Recommended, should be present if possible)
    #    OPT (Optional, can be present if useful)
    if not metadata:
        dataset_metadata = {
            "globus_subject": "https://materialsdatafacility.org/",   # REQ string: Unique value (should be URI if possible)
            "acl": ["public"],                        # REQ list of strings: UUID(s) of users/groups allowed to access data, or ["public"]
            "mdf_source_name": "surface_diffusion",   # REQ string: Unique name for dataset
            "mdf-publish.publication.collection": "Diffusion",  # RCM string: Collection the dataset belongs to
            # "mdf_data_class": ,                     # RCM string: Type of data in all records in the dataset (do not provide for multi-type datasets)
            "cite_as": ["Citation pending"],          # REQ list of strings: Complete citation(s) for this dataset.
            # "license": ,                            # RCM string: License to use the dataset (preferrably a link to the actual license).
            "dc.title": "Surface diffusion",          # REQ string: Title of dataset
            "dc.creator": "University of Illinois",   # REQ string: Owner of dataset
            "dc.identifier": "https://materialsdatafacility.org/",  # REQ string: Link to dataset (dataset DOI if available)
            # "dc.contributor.author": ,              # RCM list of strings: Author(s) of dataset
            # "dc.subject": ,                         # RCM list of strings: Keywords about dataset
            "dc.description": "Surface Diffusion Coefficients",                      # RCM string: Description of dataset contents
            # "dc.relatedidentifier": ,               # RCM list of strings: Link(s) to related materials (such as an article)
            "dc.year": 2017                           # RCM integer: Year of dataset creation
        }
    elif type(metadata) is str:
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
    dataset_validator = Validator(dataset_metadata)


    # Get the data
    #    Each record should be exactly one dictionary
    #    It is recommended that you convert your records one at a time, but it is possible to put them all into one big list (see below)
    #    It is also recommended that you use a parser to help with this process if one is available for your datatype
    try:
        # open Excel workbook
        # Note: the object is closed directly by the constructor, no need to close it
        wb = xlrd.open_workbook(input_path)

        records = run_extraction(wb)

        try:
            for record in records:
                print(json.dumps(record, indent=4, sort_keys=True))
        except IOError:
            print("A list Records is empty!")

        # Each record also needs its own metadata
        # for record in records:
        for index, record in enumerate(records, start=1):
            # Fields can be:
            #    REQ (Required, must be present)
            #    RCM (Recommended, should be present if possible)
            #    OPT (Optional, can be present if useful)
            uri = "https://materialsdatafacility.org/collection/Diffusion/" + str(index)
            record_metadata = {
                "globus_subject": uri,                     # REQ string: Unique value (should be URI to record if possible)
                "acl": ["public"],                         # REQ list of strings: UUID(s) of users/groups allowed to access data, or ["public"]
                # "mdf-publish.publication.collection": ,  # OPT string: Collection the record belongs to (if different from dataset)
                # "mdf_data_class": ,                      # OPT string: Type of data in record (if not set in dataset metadata)
                # "mdf-base.material_composition": ,       # RCM string: Chemical composition of material in record

                # "cite_as": ,                             # OPT list of strings: Complete citation(s) for this record (if different from dataset)
                # "license": ,                             # OPT string: License to use the record (if different from dataset) (preferrably a link to the actual license).

                "dc.title": record["diffusing_species"] + "/" + record["substrate"],  # REQ string: Title of record
                # "dc.creator": ,                          # OPT string: Owner of record (if different from dataset)
                # "dc.identifier": ,                       # RCM string: Link to record (record webpage, if available)
                # "dc.contributor.author": ,               # OPT list of strings: Author(s) of record (if different from dataset)
                # "dc.subject": ,                          # OPT list of strings: Keywords about record
                # "dc.description": ,                      # OPT string: Description of record
                # "dc.relatedidentifier": ,                # OPT list of strings: Link(s) to related materials (if different from dataset)
                # "dc.year": ,                             # OPT integer: Year of record creation (if different from dataset)

                "data": {                                  # RCM dictionary: Other record data (described below)
                    "raw": json.dumps(record)              # RCM string: Original data record text, if feasible
                    # "files":                             # RCM dictionary: {file_type : uri_to_file} pairs, data files (Example: {"cif" : "https://example.org/cifs/data_file.cif"})
                    }
                }

            # Pass each individual record to the Validator
            result = dataset_validator.write_record(record_metadata)

            # Check if the Validator accepted the record, and print a message if it didn't
            # If the Validator returns "success" == True, the record was written successfully
            if result["success"] is not True:
                print("Error:", result["message"], ":", result.get("invalid_metadata", ""))

        # Save your converter as [mdf_source_name]_converter.py
        # You're done!
        if verbose:
            print("Finished converting")

    except IOError:
        print("File " + input_path + " does not exist!")

def get_value(ws, wb, row, column):
    '''
    :param ws: sheet
    :param wb: workbook
    :param row: row
    :param column: column
    :return: string with the cell content
    '''
    # returns formatted string based on the Excel cell type and column
    cell_type = ws.cell_type(row, column)

    cell_value = ws.cell_value(row, column)
    # xlrd.XL_CELL_EMPTY = 0
    if cell_type == xlrd.XL_CELL_EMPTY:
        return ""
    # xlrd.XL_CELL_TEXT = 1
    elif cell_type == xlrd.XL_CELL_TEXT and len(cell_value.strip()) > 0:
        return cell_value
    # xlrd.XL_CELL_NUMBER = 2
    elif cell_type == xlrd.XL_CELL_NUMBER and cell_value != "":
        if int(cell_value) == cell_value:
            # integer
            return "{:d}".format(int(cell_value))
        else:
            if column == 13:
                # omega
                return "{:.3f}".format(cell_value)
            else:
                return "{:.2f}".format(cell_value)
    # xlrd.XL_CELL_DATE = 3
    elif cell_type == xlrd.XL_CELL_DATE:
        try:
            dt_tuple = xlrd.xldate_as_tuple(cell_value, wb.datemode)

            return "{:04d}".format(dt_tuple[0]) + "-" + "{:02d}".format(dt_tuple[1]) + "-" + "{:02d}".format(
                dt_tuple[2]) + " " + "{:02d}".format(dt_tuple[3]) + ":" + "{:02d}".format(
                dt_tuple[4]) + ":" + "{:02d}".format(dt_tuple[5])
        except ValueError:
            return ""

    # xlrd.XL_CELL_BOOLEAN = 4
    elif cell_type == xlrd.XL_CELL_BOOLEAN:
        return cell_value
    # xlrd.XL_CELL_ERROR = 5
    elif cell_type == xlrd.XL_CELL_ERROR:
        return ""
    # xlrd.XL_CELL_BLANK = 6
    elif cell_type == xlrd.XL_CELL_BLANK:
        return ""
    else:
        return ""


def get_methods(wb):
    '''
    Parse the Excel sheet with Method/Technique abbreviations.
    :param wb: workbook 
    :return: Dictionary of all methods, key is the abbr
    '''
    ws = wb.sheet_by_name('Method abbr.')
    # print ws.name, ws.nrows, ws.ncols
    methods = {}

    row_index = 0
    while row_index < ws.nrows:
        key_method = get_value(ws, wb, row_index, 0)
        value_method = get_value(ws, wb, row_index, 1)
        methods[key_method] = value_method
        row_index += 1

    return methods


def get_references(wb):
    '''
    Parse the Excel sheet with References.
    :param wb: workbook
    :return: Dictionary of all references, key is the ref number
    '''
    ws = wb.sheet_by_name('References SA95')
    # print ws.name, ws.nrows, ws.ncols
    references = {}

    row_index = 0
    while row_index < ws.nrows:
        # the first column is always an int
        cell_value = ws.cell_value(row_index, 0)
        key_ref = str(int(cell_value))
        value_ref = get_value(ws, wb, row_index, 1)
        references[key_ref] = value_ref
        row_index += 1

    return references


def run_extraction(wb):
    '''
    Parse the Surface Diffusion file. Get the data defined by the header
    'system' -> Full system of a diffusing specie on a substrate
    'diffusing_species' -> Diffusing species
    'substrate' -> Substrate
    'system_note' -> System note
    'ambient' -> Environment such as vacuum, liquid etc.
    'technique' -> Experimental technique
    'coverage_theta' -> Coverage of the diffusing specie
    'diffusion_coefficient' -> Pre-exponential factor of the diffusion coefficient (cm2s-1)
    'diffusion_coefficient_note' -> Pre-exponential factor of the diffusion coefficient note
    'activation_energy' -> Activation energy (kcal/mol)
    'activation_energy_note' -> Activation energy note
    'desorption_energy' -> Desorption energy (kcal/mol)
    'desorption_energy_note' -> Desorption energy note
    'corrugation_omega' -> Corrugation ratio Omega = Ediff/Edes
    'corrugation_omega_note' -> Corrugation ratio note
    'energy_alpha' -> Activation energy alpha= Ediff/kTm
    'energy_alpha_note' -> Activation energy alpha note
    'temperature_range' -> Temperature range relative to the substrate melting point, T/Tm
    'temperature_range_note' -> Temperature range note
    'references' -> list of References

    :param wb: A workbook of Surface Diffusion data
    :return: List of Dictionaries containing data
    '''
    # parse excel spreadsheet and create list of dictionaries with key headers
    heads = ['system', 'diffusing_species', 'substrate', 'system_note', 'ambient', 'technique', 'coverage_theta',
             'diffusion_coefficient', 'diffusion_coefficient_note', 'activation_energy', 'activation_energy_note',
             'desorption_energy', 'desorption_energy_note', 'corrugation_omega', 'corrugation_omega_note', 'energy_alpha', 'energy_alpha_note',
             'temperature_range', 'temperature_range_note', 'references']
    records = list()

    # print("The number of worksheets is", wb.nsheets)
    # print("Worksheet name(s):", wb.sheet_names())

    methods = get_methods(wb)
    references = get_references(wb)

    for sheetx in range(0, wb.nsheets - 2):
        ws = wb.sheet_by_index(sheetx)
        # print(ws.name, ws.nrows, ws.ncols)

        row_index = 0
        while row_index < ws.nrows:
            elements = list()
            papers = list()

            column_index = 0
            while column_index < 19:
                value = get_value(ws, wb, row_index, column_index)
                elements.append(value)
                column_index += 1

            if elements[0] != 'System' and elements[0] != '' and elements[1] != '' and elements[2] != '':
                elements[5] = methods[elements[5]]

                value = get_value(ws, wb, row_index, 19)
                papers.append(references['0'])
                if value != '':
                    papers_num = value.strip().split(",")
                    for paper in papers_num:
                        papers.append(references[paper.strip()])
                    elements.append(papers)

                if len(heads) == len(elements):
                    records.append(dict(zip(heads, elements)))
                else:
                    print("Wrong number of records: " + str(len(elements)) + " instead of " + str(len(heads)))

            row_index += 1
    return records


# Optionally, you can have a default call here for testing
# The convert function may not be called in this way, so code here is primarily for testing
if __name__ == "__main__":
    import paths
    convert(paths.datasets + "diffusion/Surface_Diff_Coefficients.xlsx", verbose=True)