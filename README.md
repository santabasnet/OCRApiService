## OCR API Service

An OCR service for extracting form data using predefined templates. It leverages FastAPI to provide document OCR through a RESTful interface. 

1. Image Processing
   The given image is pre-processed using homographic alignment, finds the difference of filled text using image differnce and it slices all the interested region with the help of template definition. The sample Python code to extract regions goes 
   here:
   ```Python
   # Returns the list of slices, a list of sliced image.
   def imageAlignment(_templateImage, _inputImage, pageNo):
     return ImageProcessor(_templateImage, _inputImage) \
        .findHomoGraphy() \
        .getDifference() \
        .sliceOCRAreas(pageNo)
   ```
   The OpenCV library is utilized for bounding box analysis and homographic transformation. The region of interest is extracted using:
   ```Python
   # Returns the dictionary of form field
    def sliceOCRAreas(self, pageNo) -> dict[str, list]:
        ocrFields: list[FormField] = DocumentFields.ocrFromTemplateFields(pageNo + 1)
        return {formField.getName(): self.__makeSlices(formField, pageNo) for formField in ocrFields}
   ```
   
3. Text Extraction
   ```Python
    # Execute OCR operation for all the image slices.
    # Returns the dictionary of field name and OCR output.
    def extractSlices(imageSlices, pageNo):
      # OCR done one image at a time.
      # fieldResults = {name: FieldExtraction(pageNo, name, images).extract() for (name, images) in imageSlices.items()}
      # return fieldResults
      def chunks(data, SIZE=20):
          it = iter(data)
          for i in range(0, len(data), SIZE):
              yield {k: data[k] for k in islice(it, SIZE)}
  
      # Process batch fields for the page OCR.
      # 12 for number of images in batch OCR.
      batchSlices = chunks(imageSlices, 32)
      # Display batch sizes.
      # for batch in batchSlices:
      #     print(len(batch))
      # print("\n")
  
      batchResults = [BatchExtraction(pageNo, batch).extract() for batch in batchSlices]
      # Needs to merge the list of dictionaries.
      finalResults = {k: v for x in batchResults for k, v in x.items()}
  
      return finalResults
   ```
4. An example with Tesseract OCR:
```Python
  # Extract text with Tesseract OCR.
  async def tesseractProcess(inputFile):
    fileName = secure_filename(inputFile.filename)
    filePath = os.path.join(FileUtils.UPLOAD_FOLDER, fileName)
    inputFile.save(filePath)
    inputImage = cv2.imread(filePath, cv2.IMREAD_COLOR)
    return await processImageWithTesseract(inputImage)
``` 
