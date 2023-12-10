import requests

from bdsm_project.utils.serialization import str2obj


def generate_image(text: str) -> None:
    url = "http://localhost:8087/text2img"
    tmp_image_path = "./generated.png"

    data = {"prompt": text}
    response = requests.post(url, json=data).json()
    raw_image = response["raw_image"]
    image = str2obj(raw_image)
    image.save(tmp_image_path)


if __name__ == "__main__":
    text = "Blue car with wing, 4k, photo"
    generate_image(text)
