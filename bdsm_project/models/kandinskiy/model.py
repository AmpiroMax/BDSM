import logging

import torch
from kandinsky2 import get_kandinsky2
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     [%(asctime)s][%(module)s][%(funcName)s][line %(lineno)d] - %(message)s",
    datefmt='%H:%M:%S',
)
logger = logging.getLogger("KandinskyModel")


class MyKandinsky:

    def __init__(self):
        logger.info("Initializing Kandinsky model...")
        self.kandinskiy = get_kandinsky2(
            device='cuda',
            task_type='text2img',
            model_version='2.1',
            use_flash_attention=False
        )
        logger.info("Initializing Kandinsky model - done.")

    def text2img(self, prompt: str) -> Image:
        logger.info("Generating image...")
        image = self.kandinskiy.generate_text2img(
            prompt=prompt,
            num_steps=10,
            batch_size=1,
            guidance_scale=4,
            h=512, w=512,
            sampler='p_sampler',
            prior_cf_scale=4,
            prior_steps="5"
        )[0]
        torch.cuda.empty_cache()
        logger.info("Generating image - done.")
        return image
