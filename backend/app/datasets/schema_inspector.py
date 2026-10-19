from typing import Dict, Any, List

class SchemaInspector:
    """
    Dynamically analyzes dataset records to extract present columns,
    inferred types, and candidate fields matching target schemas.
    """

    @staticmethod
    def inspect_sample_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not records:
            return {"columns": [], "sample_count": 0, "inferred_types": {}}

        columns = list(records[0].keys())
        inferred_types: Dict[str, str] = {}

        for col in columns:
            val = records[0].get(col)
            inferred_types[col] = type(val).__name__ if val is not None else "unknown"

        return {
            "columns": columns,
            "sample_count": len(records),
            "inferred_types": inferred_types,
            "first_record_preview": {k: str(v)[:100] for k, v in records[0].items()}
        }

    @staticmethod
    def find_best_field_match(record: Dict[str, Any], candidates: List[str]) -> Any:
        """
        Attempts to locate the most appropriate field from a list of prioritized candidates.
        Supports nested paths like 'answers.text[0]'.
        """
        for cand in candidates:
            if "." in cand:
                parts = cand.split(".")
                current = record
                matched = True
                for p in parts:
                    if "[" in p and p.endswith("]"):
                        field_name, idx_str = p[:-1].split("[")
                        if isinstance(current, dict) and field_name in current:
                            arr = current[field_name]
                            idx = int(idx_str)
                            if isinstance(arr, list) and len(arr) > idx:
                                current = arr[idx]
                            else:
                                matched = False
                                break
                        else:
                            matched = False
                            break
                    elif isinstance(current, dict) and p in current:
                        current = current[p]
                    else:
                        matched = False
                        break
                if matched and current is not None:
                    return current
            elif cand in record and record[cand] is not None:
                return record[cand]

        return None
