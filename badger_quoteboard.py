import badger2040
from random import randrange
from time import sleep

# Layout constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT
TEXT_PADDING = 10
TEXT_WIDTH = WIDTH - TEXT_PADDING - TEXT_PADDING

# Text constants
STARTING_SCALE = 1
FONT = "serif_italic"
THICKNESS = 2

COOLDOWN = 1

def shuffle(array):
    """Fisher–Yates shuffle
        from: https://stackoverflow.com/a/73144775
    """
    for i in range(len(array)-1, 0, -1):
        j = randrange(i+1)
        array[i], array[j] = array[j], array[i]

def display_clear(screen):
    """ Utility method to wipe the screen """
    screen.set_pen(15)
    screen.clear()
    screen.update()

# Adapted from:
# https://github.com/pimoroni/badger2040/blob/main/badger_os/examples/ebook.py
def layout(display, quote, scale):
    """ Recursively try to layout the quote given a shrinking scale """
    row = 0
    line = ""
    text_spacing = int(30 * scale)
    fit = True
    cmds = []
    words = quote.split(" ")

    while True:
        # if we're out of words we're done!
        if len(words) == 0:
            break

        word = words.pop(0).strip()
        #print("word is", word)

        # Append the word to the current line and measure its length
        appended_line = line
        if len(line) > 0 and len(word) > 0:
            appended_line += " "
        appended_line += word
        appended_length = display.measure_text(appended_line, scale)

        # Would this appended line be longer than the text display area:
        if appended_length >= TEXT_WIDTH:

            # Yes, so write out the line prior to the append
            cmds.append(
                    (line,
                     TEXT_PADDING,
                     (row * text_spacing) + (text_spacing // 2) + TEXT_PADDING,
                     WIDTH,
                     scale)
                )

            # Clear the line and move on to the next row
            line = ""
            row += 1

            # Have we reached the end of the page?
            if (row * text_spacing) + text_spacing >= HEIGHT:
                fit = False
                break

            else:
                # Set the line to the word
                line = word

        else:
            # The appended line was not too long, so set it as the line and
            # advance the current position
            line = appended_line
            if len(words) == 0:
                break

    if fit:
        # store the final line
        cmds.append(
                (line,
                 TEXT_PADDING,
                 (row * text_spacing) + (text_spacing // 2) + TEXT_PADDING,
                 WIDTH,
                 scale)
            )

        return cmds

    # If it doesn't fit (we overflowed the page) try again with a smaller scale
    # TODO: binary search?
    scale = scale * 0.9
    return layout(display, quote, scale)

def draw_quote(display, quote, scale):
    """ Draw a quote at the maximum size """
    cmds = layout(display, quote, scale)
    display_clear(display)
    display.set_pen(0)
    for cmd in cmds:
        display.text(*cmd)
    display.update()

def main():
    """ Entry point"""

    # initialize badger settings
    screen = badger2040.Badger2040()
    screen.set_thickness(THICKNESS)
    screen.set_font(FONT)

    # load the quotes
    with open("quotes.txt") as f:
        lines = f.readlines()

    shuffle(lines)
    index = 0

    # shuffle everyone up!
    while True:

        # pick the quote
        quote = lines[index]
        print("quote %s: %s" % (index, quote))

        # Draw the quote
        draw_quote(screen, "\"%s\"" % quote, STARTING_SCALE)

        # Fade out the LED
        # has the effect of a cooldown as these calls block!
        for i in reversed(range(255)):
            screen.led(i)
            sleep(COOLDOWN)

        # TODO: this behaves different on usb power vs. battery...
        # might need to change screen.pressed(), below, into
        # screen.woken_by_button()
        screen.halt()

        # Process button presses!
        if screen.pressed(badger2040.BUTTON_UP):
            index = (index + 1) % len(lines)

        elif screen.pressed(badger2040.BUTTON_DOWN):
            index = (index - 1) % len(lines)

        # Go to a random index!
        elif any(screen.pressed(b) for b in [badger2040.BUTTON_A,
                                            badger2040.BUTTON_B,
                                            badger2040.BUTTON_C]):
            index = randrange(0, len(lines))


if __name__ == "__main__":
    main()
