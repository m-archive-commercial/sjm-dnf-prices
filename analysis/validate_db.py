"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 24, 2022, 16:58
"""
from collections import OrderedDict
from pprint import pprint

from base import db

vexpr = {
    "collMod"         : "price",
    "validator"       : {
        "$jsonSchema": {
            "bsonType"  : "object",
            "required"  : ["category", "data", "name"],
            "properties": {
                "data": {
                    "properties": {
                        "xAxis" : {
                            "bsonType": "array",
                            "minItems": 1,
                            "maxItems": 1
                        },
                        "series": {
                            "bsonType"   : "array",
                            "minItems"   : 3,
                            "maxItems"   : 3,
                            "uniqueItems": True,
                            "items"      : {
                                "properties": {
                                    "name": {
                                        "enum": [
                                            "低价",
                                            "平均价",
                                            "高价"
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "validationLevel" : "strict",
    "validationAction": "error"
}

set_validation_result = db.command(OrderedDict(vexpr))

validated_result = db .validate_collection('price')

pprint({
    "set_validation_result": set_validation_result,
    "validated_result"     : validated_result
})

assert len(validated_result['warnings']) == 0 and len(validated_result['errors']) == 0
# TODO: why no errors, instead of warnings ?

# check log if validated result has `warnings` or `errors`
# client.admin.command( { "getLog": "global" } )
