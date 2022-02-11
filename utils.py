from pyrenaper import Renaper, Sid
from pyrenaper.environments import ONBOARDING, SID
import os

renaper = Renaper(ONBOARDING,
                  os.environ['PAQUETE1_API_KEY'],
                  os.environ['PAQUETE2_API_KEY'],
                  os.environ['PAQUETE3_API_KEY'])
sid = Sid(SID,
          username=os.environ['USERNAME'],
          password=os.environ['PASSWORD'])

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
    
def call_sid_api(method, *args, **kwargs):
    sid.login()
    try:
        data = getattr(sid, method)(*args, **kwargs)
    except Exception as e:
        return {"status": False, "error": e.__class__.__name__, "description": e.__str__()}, 500
    return data, 200
