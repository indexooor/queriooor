from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
import json
from models.querier import StorageLayoutAdd, Querier, QuerySlot
from models.api import ResponseModel, ErrorResponseModel
from utils.utils import getStorageSlot, getSlotValue, FetchObj


router = APIRouter()

# Pydantic typing is left for routes


@router.get("/test", response_description="test route for queriooor")
async def test():
    return {"message": "Welcome to Indexooor Querier Rest API!"}


# setStoageLayout end takes storage layout json as param and saves it as json on filesystem
@router.post(
    "/setStorageLayout",
    response_description="Set storage layout for contract address for which querier will fetch and decode data",
)
async def set_storage_layout(
    storageLayout: StorageLayoutAdd = Body(...),
):
    # save dictionary as json file with name contractAddress
    with open("./files/" + storageLayout.contractAddress + ".json", "w") as outfile:
        storageLayout.storageLayout["primaryClass"] = storageLayout.primaryClass
        json.dump(storageLayout.storageLayout, outfile)

    return ResponseModel(
        data=storageLayout.storageLayout,
        message="Storage layout added successfully!",
    )


@router.post(
    "/getVariable",
    response_description="Get variable value from indexed slot database (decoding it using type from storage layout)",
)
async def get_variable(
    data: Querier = Body(...),
):
    try:
        # get storage slot
        name, slot, size, offset, typeStr = getStorageSlot(
            data.contractAddress,
            data.targetVariable,
            key=data.key,
            deepKey=data.deepKey,
            structVar=data.structVar,
        )

        # get slot value
        slotValue = getSlotValue(
            contractAddress=data.contractAddress,
            slot=slot,
            offset=offset,
            size=size,
            typeStr=typeStr,
        )

        saveObj = FetchObj(data.contractAddress)
        # change the key thing here, as this may lead to bugs when user adds key to body for variables without key
        saveObj.addVariableName(
            slot,
            data.targetVariable,
            key=data.key,  # buggy, find datatype and store key if data type should have key
            deepKey=data.deepKey,  # buggy, find datatype and store deep key if data type should have deep key
            structVar=data.structVar,  # buggy, find datatype and store structVar if data type should have structVar
        )

        return ResponseModel(
            data={
                "variableName": data.targetVariable,
                "variableValue": slotValue,
                "variableType": typeStr,
            },
            message="Variable fetched successfully!",
        )
    except Exception as e:
        # raise e

        return ErrorResponseModel(
            error=str(e),
            code=500,
            message="An error occurred",
        )


@router.post(
    "/getSlot",
    response_description="Get slot value from indexed slot database",
)
async def get_slot(
    data: QuerySlot = Body(...),
):
    try:
        # Directly fetch slot value from storage slot and return

        slot = data.slot

        fetch = FetchObj(data.contractAddress)

        fetchedData = fetch.getDirectSlotData(slot)

        return ResponseModel(
            data={slot: fetchedData},
            message="Slot fetched successfully!",
        )

    except Exception as e:
        # raise e

        return ErrorResponseModel(
            error=str(e),
            code=500,
            message="An error occurred",
        )
