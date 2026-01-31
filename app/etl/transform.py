from typing import Dict, Any, Tuple, List

from app.models.mobility import RawTripRow, StagedTrip

def validate_row(raw_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    raw_model = RawTripRow(**raw_dict)

    raw_dump = raw_model.model_dump(by_alias=True)

    staged = StagedTrip.model_validate(raw_dump)
    staged_dump = staged.model_dump()

    return raw_dump, staged_dump