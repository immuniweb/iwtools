#! /usr/bin/env python3

class InfiniteLoader:
    """Animated loader builder"""

    direction = 1
    length = 0


    def __init__(self, length):
        self.length = length


    def ease_in_out(self, time, start, end, duration):
        """EaseInOut easing function"""

        time /= duration / 2

        if time < 1:
            return end / 2 * time * time + start

        time -= 1

        return -end / 2 * (time * (time - 2) - 1) + start


    def generate(self, step):
        """Generate ASCII loader"""

        bar_length = self.length - 4
        progress_length = 5
        free_bar = bar_length - progress_length

        fill = step % free_bar
        fill_percent = fill / free_bar
        fill_ease = round(self.ease_in_out(fill_percent, 0, free_bar, 1))

        if self.direction > 0:
            bar_left = fill_ease
        else:
            bar_left = free_bar - fill_ease

        bar_right = bar_length - (bar_left + progress_length)

        if fill == free_bar - 1:
            self.direction *= -1

        bar = ' ' * bar_left + '=' * progress_length + ' ' * bar_right
        loader = ' [' + bar + '] '

        return loader
