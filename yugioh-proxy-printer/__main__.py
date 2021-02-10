from dataclasses import dataclass
from typing import IO, List, Optional

import argparse
import pathlib
import sys
import urllib.request

import pdflatex
import ygoprodeck


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("ydk_filepath")

    args = parser.parse_args(argv)

    ygo = ygoprodeck.YGOPro()
    image_cache = ImageCache(pathlib.Path("images"))

    with open(args.ydk_filepath, "r") as input_stream:
        card_ids = parse_ydk_file(input_stream)

    card_images = []
    for card_id in card_ids:
        card_name = get_card_name_by_id(ygo, card_id)
        assert card_name is not None

        card_image = image_cache.get_image(ygo, card_name)
        card_images.append(card_image)

    with open("cards.tex", "w") as output_stream:
        write_cards_tex(output_stream, card_images)

    pdfl = pdflatex.PDFLaTeX.from_texfile("deck.tex")
    pdf, log, completed_process = pdfl.create_pdf(
        keep_pdf_file=True, keep_log_file=True
    )


def write_cards_tex(output_stream: IO[str], card_images: List[pathlib.Path]) -> None:
    for i, path in enumerate(card_images):
        output_stream.write(f"\\card{{{path}}}\n")

        if i % 3 == 2:
            # Add in a newline, but with less spacing
            output_stream.write("\\\\[-2mm]\n")


def get_card_name_by_id(ygo: ygoprodeck.YGOPro, card_id: int) -> Optional[str]:
    matches = ygo.get_cards(id=card_id)["data"]

    if len(matches) == 0:
        return None

    assert len(matches) == 1

    return matches[0]["name"]


def parse_ydk_file(input_stream: IO[str]) -> List[int]:
    # TODO: See if there is an actual spec for this file format
    card_ids = []
    for line in input_stream:
        line = line.split("#")[0]
        line = line.split("!")[0]

        if len(line) > 0:
            card_id = int(line)

            card_ids.append(card_id)

    return card_ids


@dataclass
class ImageCache:
    cache_path: pathlib.Path

    def __get_card_filepath(self, card_name: str) -> pathlib.Path:
        return self.cache_path.joinpath(f"{card_name}.jpg")

    def get_image(self, ygo: ygoprodeck.YGOPro, card_name: str) -> pathlib.Path:
        filepath = self.__get_card_filepath(card_name)

        if not filepath.exists():
            self.cache_path.mkdir(parents=True, exist_ok=True)
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
