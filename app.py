from pyrenaper.models import Selfie
from pyrenaper.utils import BarcodeReader
from utils import call_renaper_api, call_sid_api
from parsers import *
from flask_restful import Resource, Api
from flask import Flask, request
from PIL import Image
from io import BytesIO
import json
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)

class DefaultRenaperView(Resource):
    parser = None
    method = None

    def _get_extra_data(self):
        raise NotImplementedError

    def post(self):
        args = self.parser.parse_args()
        extra_args, extra_kwargs = self._get_extra_data(args)
        return call_renaper_api(self.method, *extra_args, **extra_kwargs)


class PersonData(DefaultRenaperView):
    parser = person_data_parser
    method = 'person_data'

    def _get_extra_data(self, args):
        return [args['number'], args['gender'], args['order']], {}


class NewOperation(DefaultRenaperView):

    parser = new_operation_parser
    method = 'new_operation'

    def _get_extra_data(self, args):
        return [args['number'], args['gender'], args['ip'], args['browser_fingerprint']], {}


class AddBack(DefaultRenaperView):
    parser = add_image_parser
    method = 'add_back'

    def _get_extra_data(self, args):
        extra_data = {}
        if args.get('analyze_anomalies'):
            extra_data['analyze_anomalies'] = args['analyze_anomalies']
        if args.get('analyze_ocr'):
            extra_data['analyze_ocr'] = args['analyze_ocr']
        return [args['operation_id'], args['number'], args['gender'], args['file']], extra_data


class AddFront(AddBack):
    method = 'add_front'


class Register(DefaultRenaperView):

    parser = register_parser
    method = 'register'

    def _get_extra_data(self, args):
        selfies = [Selfie(selfie['file'], selfie['image_type']) for selfie in json.loads(args['selfie_list'])]
        if len(selfies) == 0:
            return {"error": 'InvalidSelfieList', "description": "Please provide at least 1 selfie"}, 400
        return [args['operation_id'], args['gender'], args['number'], selfies], {}


class AddBarcode(DefaultRenaperView):

    parser = add_barcode_parser
    method = 'add_barcode'

    def _get_extra_data(self, args):
        document = json.loads(args['document'])
        return [args['operation_id'], args['number'], args['gender'], document], {}


class ScanBarcode(DefaultRenaperView):

    parser = scan_barcode_parser
    method = 'scan_barcode'

    def _get_extra_data(self, args):
        return [args['file']], {}

class EndOperation(DefaultRenaperView):

    parser = end_operation_parser
    method = 'end_operation'

    def _get_extra_data(self, args):
        return [args['operation_id'], args['number'], args['gender']], {}

class FaceLogin(DefaultRenaperView):

    parser = face_login_parser
    method = 'face_login'

    def _get_extra_data(self, args):
        selfies = [Selfie(selfie['file'], selfie['image_type']) for selfie in json.loads(args['selfie_list'])]
        if len(selfies) == 0:
            return {"error": 'InvalidSelfieList', "description": "Please provide at least 1 selfie"}, 400
        return [args['number'], args['gender'], selfies, args['browser_fingerprint']], {}



class EncodeImages(Resource):
    parser = image_encoder_parser
    args = None

    def convertImageFormat(self, image):
        bytes_io_image = BytesIO()
        image.save(bytes_io_image, 'JPEG')
        byte_data = bytes_io_image.getvalue()
        return base64.b64encode(byte_data).decode()

    def _resize(self, image, width, height=None):
        image = Image.open(image)
        if not height:
            wpercent = (width / float(image.size[0]))
            height = int((float(image.size[1]) * float(wpercent)))

        new_img = image.resize((width, height), Image.ANTIALIAS)
        return self.convertImageFormat(new_img)

    def post(self):
        args = self.parser.parse_args()
        back = self._resize(args['back'], 1200)
        front = self._resize(args['front'], 1200)
        selfie = self._resize(args['selfie'], 600, height=600)
        return {"back": back, "front": front, "selfie": selfie}


class PackageOneView(EncodeImages):
    parser = full_package_one_parser

    def post(self):
        data = super(PackageOneView, self).post()
        ip_address = request.remote_addr
        scan_barcode_response, status = call_renaper_api('scan_barcode', data['front'])
        if scan_barcode_response['status']:
            barcode_data = scan_barcode_response['response']['data']
            user_data = dict(number=barcode_data['number'], gender=barcode_data['gender'])
            new_operation_response, status = call_renaper_api('new_operation',
                                                              user_data['number'],
                                                              user_data['gender'],
                                                              ip_address,
                                                              '')
                                                              #self.args['browser_fingerprint'])
            if new_operation_response['status']:
                operation_id = new_operation_response['response']['operationId']
                add_barcode_response, status = call_renaper_api('add_barcode',
                                                                operation_id,
                                                                user_data['number'],
                                                                user_data['gender'],
                                                                barcode_data)
                if add_barcode_response['status']:
                    add_front_response, status = call_renaper_api('add_front',
                                                                  str(operation_id),
                                                                  user_data['number'],
                                                                  user_data['gender'],
                                                                  data['front'])

                    if add_front_response['status']:
                        add_back_response, status = call_renaper_api('add_back',
                                                                     operation_id,
                                                                     user_data['number'],
                                                                     user_data['gender'],
                                                                     data['back'])
                        if add_back_response['status']:
                            selfies = [Selfie(data['selfie'], 'SN')]
                            register_response, status = call_renaper_api('register',
                                                                         operation_id,
                                                                         user_data['gender'],
                                                                         user_data['number'],
                                                                         selfies)
                            if register_response['status']:
                                end_operation_response = call_renaper_api('end_operation',
                                                                          operation_id,
                                                                          user_data['number'],
                                                                          user_data['gender'],
                                                                          )
                                return end_operation_response
                            else:
                                return register_response
                        else:
                            return add_back_response
                    else:
                        return add_front_response
                else:
                    return add_barcode_response
            else:
                return new_operation_response
        else:
            return scan_barcode_response


class SidFullApi(Resource):
    parser = sid_parser
    args = None

    def convertImageFormat(self, image):
        bytes_io_image = BytesIO()
        image.save(bytes_io_image, 'JPEG')
        byte_data = bytes_io_image.getvalue()
        return base64.b64encode(byte_data).decode()

    def _resize(self, image, width, height=None):
        image = Image.open(image)
        if not height:
            wpercent = (width / float(image.size[0]))
            height = int((float(image.size[1]) * float(wpercent)))

        new_img = image.resize((width, height), Image.ANTIALIAS)
        return self.convertImageFormat(new_img)

    def post(self):
        args = self.parser.parse_args()
        front = self._resize(args['front'], 1200)
        barcode_reader = BarcodeReader()
        user_data = barcode_reader.get_barcode_payload(front)
        return call_sid_api('get_full_person_data', user_data['number'],
                                                     user_data['gender'],
                                                     user_data['order'])



api.add_resource(PersonData, '/person_data')
api.add_resource(FaceLogin, '/face_login')
api.add_resource(NewOperation, '/new_operation')
api.add_resource(AddBack, '/add_back')
api.add_resource(AddFront, '/add_front')
api.add_resource(Register, '/register')
api.add_resource(AddBarcode, '/add_barcode')
api.add_resource(ScanBarcode, '/scan_barcode')
api.add_resource(EndOperation, '/end_operation')
api.add_resource(EncodeImages, '/encode_images')
api.add_resource(PackageOneView, '/packageone')
api.add_resource(SidFullApi, '/sid')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
