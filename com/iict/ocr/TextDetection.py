# Utility class for the text detection mechanism.

from craft_text_detector import Craft
from craft_text_detector import (
    load_craftnet_model,
    load_refinenet_model,
    get_prediction
)

# load models
refine_net = load_refinenet_model(cuda=False)
craft_net = load_craftnet_model(cuda=False)


class TextDetection:
    # Default constructor, receives the numpy image.
    def __init__(self, _sourceImage):
        self._sourceImage = _sourceImage

    # Returns the detected bounding images, i.e. list of images.
    def detect(self):
        # Make prediction here.
        prediction_result = get_prediction(
            image=self._sourceImage,
            craft_net=craft_net,
            refine_net=refine_net,
            text_threshold=0.5,
            link_threshold=0.1,
            low_text=0.1,
            cuda=False,
            long_size=1280
        )
        images = []
        for i, j in enumerate(prediction_result['boxes']):
            roi = self._sourceImage[int(prediction_result['boxes'][i][0][1]): int(prediction_result['boxes'][i][2][1]),
                  int(prediction_result['boxes'][i][0][0]): int(prediction_result['boxes'][i][2][0])]
            images.append(roi)

        return images
