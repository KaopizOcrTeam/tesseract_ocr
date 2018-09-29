import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=str, required=True, help='Path to output file')
parser.add_argument('--chars_per_row', type=int, default=50, help='Number of characters per row')


def write_character_block(file, char_block, chars_per_row):
        text_length = 0
        text = ''
        for char_code in char_block:
            text += chr(char_code) + ' '
            text_length += 2

            if text_length >= chars_per_row:
                file.write('{}\n'.format(text))
                text = ''
                text_length = 0

        if text_length > 0:
            file.write('{}\n'.format(text))


if __name__ == '__main__':
    args = parser.parse_args()
    output = args.output
    chars_per_row = args.chars_per_row

    punc_chars = range(0x3000, 0x3040)
    hiragana_chars = range(0x3040, 0x30a0)
    katakana_chars = range(0x30A0, 0x3100)
    full_width_roman_half_width_katakana_chars = range(0xff00, 0xfff0)
    kanji_chars = range(0x4e00, 0x9fb0)

    # TODO write all hiragana, katakana and kanji characters to output file
    with open(output, 'w') as f:
        # Write punctuations
        write_character_block(f, punc_chars, chars_per_row)

        # Write hiraganas
        write_character_block(f, hiragana_chars, chars_per_row)

        # Write katakanas
        write_character_block(f, katakana_chars, chars_per_row)

        # Write full-width romaji and half-width katakana
        write_character_block(f, full_width_roman_half_width_katakana_chars, chars_per_row)

        # Write kanji
        write_character_block(f, kanji_chars, chars_per_row)

