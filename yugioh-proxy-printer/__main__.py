from typing import List

import sys

import ygoprodeck


def main(args: List[str]) -> None:
    print(args)

    ygo = ygoprodeck.YGOPro()

    print(ygo.get_cards(name="Dark Magician")["data"][0]["card_images"][0]["image_url"])


if __name__ == "__main__":
    main(sys.argv[1:])
