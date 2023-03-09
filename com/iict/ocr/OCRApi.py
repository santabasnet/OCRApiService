# Model Utilities.

from transformers import (
    TrOCRConfig,
    TrOCRProcessor,
    TrOCRForCausalLM,
    ViTConfig,
    ViTModel,
    VisionEncoderDecoderModel,
)

from com.iict.ocr.BetterHFTrOCR import BetterHFTrOCR


class Document:

    def __init__(self):
        print("1. Initialize OCR Model ...")

        # TrOCR is a decoder self.model and should be used within a VisionEncoderDecoderModel
        # init vision2text self.model with random weights
        # encoder = ViTModel(ViTConfig())
        # decoder = TrOCRForCausalLM(TrOCRConfig())
        # self.model = VisionEncoderDecoderModel(encoder=encoder, decoder=decoder)
        # self.model = BetterHFTrOCR(model_path="assets/trained_model", ).to('cpu')
        # self.processor = TrOCRProcessor.from_pretrained("assets/processor")

        self.model = BetterHFTrOCR(model_path="microsoft/trocr-base-handwritten", ).to('cpu')
        self.processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
        self.configure_generation()

        # If you want to start from the pretrained self.model, load the checkpoint with `VisionEncoderDecoderModel`
        # self.model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

        print("2. OCR self.model loaded successfully.")

    def configure_generation(self, beams=1):
        # self.model.config.decoder_start_token_id = preprocessor.tokenizer.cls_token_id # only if you're going to train
        # the self.model
        self.model.config.pad_token_id = self.model.config.decoder.pad_token_id = self.processor.tokenizer.pad_token_id
        self.model.config.eos_token_id = self.model.config.decoder.eos_token_id = self.processor.tokenizer.sep_token_id
        # make sure vocab size is set correctly
        self.model.config.vocab_size = self.model.config.decoder.vocab_size
        # set beam search parameters
        self.model.config.decoder.early_stopping = True
        self.model.config.decoder.no_repeat_ngram_size = 3
        self.model.config.decoder.length_penalty = 2.0
        self.model.config.decoder.num_beams = beams

        # configure_generation(cuda_hf_model, 1)
        # configure_generation(cpu_hf_model, 1)

    # image is of type PIL image.
    def extract(self, image) -> list:
        # pixel_values = self.processor(image, return_tensors="pt").pixel_values
        pixel_values = self.processor.image_processor(image, return_tensors="pt").pixel_values
        # generated_ids = self.model.generate(pixel_values)
        generated_texts = self.processor.tokenizer.batch_decode(
            self.model.generate(pixel_values.to('cpu'), max_length=64), skip_special_tokens=True
        )
        return generated_texts

    def extractSegments(self, image) -> list[list[str]]:
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        generated_ids = self.model.generate(
            pixel_values,
            return_dict_in_generate=True,
            num_beams=6,
            num_beam_groups=2,
            num_return_sequences=4,
            output_scores=True)

        # 1. Accumulate all the string segments.
        allBeams = [[self.processor.decode(index) for index in items] for items in generated_ids[0]]

        # 2. Compose with list of sub-strings and get unique ones using map values.
        allSegments = list({''.join(grams): grams for grams in allBeams}.values())

        # 3. Perform filter operation of segments tag '</s>'.
        result = [[segment for segment in segments if segment != '</s>'] for segments in allSegments]

        return result
