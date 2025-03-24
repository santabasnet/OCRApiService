from transformers import AutoConfig, VisionEncoderDecoderModel
import torch
from transformers.modeling_outputs import Seq2SeqLMOutput


class BetterHFTrOCR(VisionEncoderDecoderModel):
    """creates a TrOCR model"""

    def __init__(self, model_path):
        model_ = VisionEncoderDecoderModel.from_pretrained(model_path)
        super().__init__(model_.config)
        self.encoder = model_.encoder
        self.decoder = model_.decoder

    def forward(
            self,
            pixel_values=None,
            decoder_input_ids=None,
            decoder_attention_mask=None,
            encoder_outputs=None,
            past_key_values=None,
            decoder_inputs_embeds=None,
            labels=None,
            use_cache=None,
            output_attentions=None,
            output_hidden_states=None,
            return_dict=None,
            **kwargs,
    ):

        encoder_hidden_states = encoder_outputs['last_hidden_state'] \
            if type(encoder_outputs) == dict \
            else encoder_outputs[0]

        encoder_attention_mask = None

        eos_mask = decoder_input_ids[:, -1] <= self.config.eos_token_id

        # Decode
        if any(eos_mask) and (decoder_input_ids.shape[1] > 1):
            reduced_logits = self.decoder(
                ### compute reduction ###
                input_ids=decoder_input_ids[torch.logical_not(eos_mask), :],
                attention_mask=decoder_attention_mask[torch.logical_not(eos_mask), :],
                encoder_hidden_states=encoder_hidden_states[torch.logical_not(eos_mask), :, :],
                #########################
                encoder_attention_mask=encoder_attention_mask,
                inputs_embeds=decoder_inputs_embeds,
                output_attentions=output_attentions,
                output_hidden_states=output_hidden_states,
                use_cache=use_cache,
                past_key_values=past_key_values,
            ).logits

            logits = torch.full(
                (decoder_input_ids.shape[0], decoder_input_ids.shape[1], self.config.decoder.vocab_size),
                fill_value=self.config.pad_token_id, dtype=reduced_logits.dtype, device=reduced_logits.device)
            logits[torch.logical_not(eos_mask), :, :] = reduced_logits
            logits[eos_mask, :, :] = self.ids_to_logits(decoder_input_ids[eos_mask, 1:], reduced_logits)
        else:
            logits = self.decoder(
                input_ids=decoder_input_ids,
                attention_mask=decoder_attention_mask,
                encoder_hidden_states=encoder_hidden_states,
                encoder_attention_mask=encoder_attention_mask,
                inputs_embeds=decoder_inputs_embeds,
                output_attentions=output_attentions,
                output_hidden_states=output_hidden_states,
                use_cache=use_cache,
                past_key_values=past_key_values,
            ).logits

        return Seq2SeqLMOutput(
            logits=logits,
        )

    def ids_to_logits(self, ids, reduced_logits):
        logits = torch.zeros((ids.shape[0], ids.shape[1] + 1, self.config.decoder.vocab_size),
                             dtype=reduced_logits.dtype, device=reduced_logits.device)
        logits[:, -1, 2] = 1  # max_pad_token
        for i in range(ids.shape[1]):
            logits[:, i, ids[:, i]] = 1

        return logits

    # better_cuda_hf_trocr = BetterHFTrOCR(
    #     model_path='microsoft/trocr-small-handwritten',
    #     ).to('cuda')

    # better_cpu_hf_trocr = BetterHFTrOCR(
    #     model_path='microsoft/trocr-small-handwritten',
    #     ).to('cpu')

    # # configure_generation(better_cuda_hf_trocr)
    # configure_generation(better_cpu_hf_trocr)
