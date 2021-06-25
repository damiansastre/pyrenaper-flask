from pyrenaper import Renaper
from pyrenaper.environments import ONBOARDING
import os

renaper = Renaper(ONBOARDING,
                  os.environ['PAQUETE1_API_KEY'],
                  os.environ['PAQUETE2_API_KEY'],
                  os.environ['PAQUETE3_API_KEY'])


def call_renaper_api(method, *extra_args, **extra_kwargs):
    try:
        data = getattr(renaper, method)(*extra_args, **extra_kwargs)
    except Exception as e:
        return {"status": False, "error": e.__class__.__name__, "description": e.__str__()}, 500
    else:
        if not data.status:
            return {"status": False,
                    "error": {"response": data.response['message'],
                              "code": data.code,
                              "description": data.code_description}}, 400
        else:
            return data.json, 200