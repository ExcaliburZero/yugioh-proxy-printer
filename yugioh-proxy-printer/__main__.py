from dataclasses import dataclass
from typing import List

import pathlib
import sys
import urllib.request

import ygoprodeck


def main(args: List[str]) -> None:
    print(args)

    ygo = ygoprodeck.YGOPro()
    image_cache = ImageCache(pathlib.Path("images"))

    print(image_cache.get_image(ygo, "Dark Magician"))


@dataclass
class ImageCache:
    cache_path: pathlib.Path

    def __get_card_filepath(self, card_name: str) -> str:
        return self.cache_path.joinpath(f"{card_name}.jpg")

    def get_image(self, ygo: ygoprodeck.YGOPro, card_name: str) -> str:
        filepath = self.__get_card_filepath(card_name)

        if not filepath.exists():
            self.__download_image(ygo, card_name, filepath)
            assert filepath.exists()

        return filepath

    def __download_image(
        self, ygo: ygoprodeck.YGOPro, card_name: str, filepath: pathlib.Path
    ) -> None:
        card = ygo.get_cards(name=card_name)

        image_url = card["data"][0]["card_images"][0]["image_url"]
        urllib.request.urlretrieve(image_url, filepath)


if __name__ == "__main__":
    main(sys.argv[1:])
