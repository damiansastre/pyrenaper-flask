from flask_restful import reqparse
import werkzeug

base_data_parser = reqparse.RequestParser()
base_data_parser.add_argument('number', type=str, required=True, help='User DNI')
base_data_parser.add_argument('gender', type=str, required=True, help='Sexo: F/M', choices=('M', 'F'))


face_login_parser = base_data_parser.copy()
face_login_parser.add_argument('selfie_list', type=str, required=True, help='List of Selfie Images')
face_login_parser.add_argument('browser_fingerprint', required=True, type=str, help='Browser Fingerprint Provided by JS lib.')

person_data_parser = base_data_parser.copy()
person_data_parser.add_argument('order', type=str, required=True, help='Numero de Tramite')

new_operation_parser = base_data_parser.copy()
new_operation_parser.add_argument('ip', type=str, required=True, help='Ip del CLiente')
new_operation_parser.add_argument('browser_fingerprint', required=True, type=str, help='Browser Fingerprint Provided by JS lib.')


base_package1_parser = base_data_parser.copy()
base_package1_parser.add_argument('operation_id', type=str, required=True, help='Operation ID')

end_operation_parser = new_operation_parser.copy()

add_image_parser = base_package1_parser.copy()
add_image_parser.add_argument('file', type=str, required=True, help='BASE64 image file of back of ID')
add_image_parser.add_argument('analyze_anomalies', type=bool, required=False, help='Look for anomalies')
add_image_parser.add_argument('analyze_ocr', type=bool, required=False, help='Analyze OCR')

register_parser = base_package1_parser.copy()
register_parser.add_argument('selfie_list', type=str, required=True, help='List of Selfie Images')

add_barcode_parser = base_package1_parser.copy()
add_barcode_parser.add_argument('document', type=str, required=True, help='Document Dict.')

image_encoder_parser = reqparse.RequestParser()
image_encoder_parser.add_argument('front', type=werkzeug.datastructures.FileStorage, location='files', required=True)
image_encoder_parser.add_argument('back', type=werkzeug.datastructures.FileStorage, location='files', required=True)
image_encoder_parser.add_argument('selfie', type=werkzeug.datastructures.FileStorage, location='files', required=True)

full_package_one_parser = image_encoder_parser.copy()
full_package_one_parser.add_argument('browser_fingerprint', type=str, required=True, help='Browser Finger Print')

scan_barcode_parser = reqparse.RequestParser()
scan_barcode_parser.add_argument('file', type=str, required=True, help='Image Containing PDF417 QR Code.')
