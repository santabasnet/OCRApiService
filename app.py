# Image Utilities.
from flask import Flask, request
from flask_cors import CORS

from com.iict.ocr import FileUtils, TextExtraction, Reports

# Global objects for image utilities.
app = Flask(__name__)
CORS(app)

# Route mapped to the root link.
@app.route('/', methods=['GET'])
async def textExtraction():  # put application's code here
    #return await TextExtraction.staticProcess()
    return "Use : http://18.218.208.15:5000/ocr and put pdf file in the form-data with POST request for OCR."


@app.route('/ocr', methods=['POST'])
async def fileOCR():
    if 'file' not in request.files:
        return Reports.noFileError()
    else:
        inputFile = request.files['file']
        if FileUtils.isValid(inputFile):
            return await TextExtraction.saveAndProcess(inputFile)
        else:
            return Reports.invalidFileError()


@app.route('/tocr', methods=['POST'])
async def tFileOCR():
    if 'file' not in request.files:
        return Reports.noFileError()
    else:
        inputFile = request.files['file']
        if FileUtils.isValid(inputFile):
            return await TextExtraction.tesseractProcess(inputFile)
        else:
            return Reports.invalidFileError()


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
