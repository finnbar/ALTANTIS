from typing import List, Tuple, Any

def list_to_and_separated(items : List[Any]) -> str:
    if len(items) == 0:
        return ""
    if len(items) == 1:
        return items[0]
    # Turn into a list with commas to separate elements.
    result = []
    for item in items:
        result.append(item)
        result.append(", ")
    # Then remove the last comma and replace the second last comma with " and "
    result = result[:-1]
    result[-2] = " and "
    return "".join(result)

def to_titled_list(items : List[str]) -> str:
    return list_to_and_separated(list(map(lambda x: x.title(), items)))

def to_pair_list(items : List[Any]) -> List[Tuple[Any, Any]]:
    pairs = []
    if len(items) % 2 == 1:
        raise ValueError("Input list is badly formatted.")
    for i in range(0, len(items), 2):
        pairs.append((items[i], int(items[i+1])))
    return pairs
