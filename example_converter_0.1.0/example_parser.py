import random
from bson import ObjectId


# EXAMPLE FUNCTION
# Input: single record
# Output: single record
def parse_example_single(data):
    random.seed(str(data))
    result = {
        "useful_data_1": random.random(),
        "useful_data_2": random.randint(0, 10),
        "useful_data_3": random.randint(10, 20),
        "superfluous_data": "2 + 2 = 4",
        "chemical_composition": "Og4UueC1",
        "id": str(ObjectId())
        }
    return result


# EXAMPLE FUNCTION
# Input: single record
# Output: yields many records
def parse_example_list(data):
    try:
        count = int(data)
    except Exception:
        try:
            count = len(data)
        except Exception:
            count = 10
    for i in range(count):
        yield parse_test_single(i)


if __name__ == "__main__":
    print("\nThis is an example parser.\nUSAGE:")
    print("\nparse_example_string(data)")
    print("Arguments:\n\tdata: Any data")
    print("Returns: A single result as a dict")
    print("\nparse_example_list(data)")
    print("Arguments:\n\tdata: Any data")
    print("Returns: Multiple results as dicts, yielded")
