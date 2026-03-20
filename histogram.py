import math


class Histogram:
    def __init__(
        self, bins: int, range_min: float, range_max: float, scale: str = "linear"
    ):
        self.bins = bins
        self.min = range_min
        self.max = range_max
        self.scale = scale.lower()
        self.counts = [0] * bins

        if self.scale == "log" and self.min <= 0:
            raise ValueError("Min range must be > 0 for log scale.")

    def _get_bin_index(self, value: float) -> int:
        if not (self.min <= value <= self.max):
            return -1

        if self.scale == "log":
            norm_val = (math.log(value) - math.log(self.min)) / (
                math.log(self.max) - math.log(self.min)
            )
        else:
            norm_val = (value - self.min) / (self.max - self.min)

        idx = int(norm_val * self.bins)
        return min(idx, self.bins - 1)

    def add(self, value: float):
        """Increments the count for the bin containing value."""
        idx = self._get_bin_index(value)
        if idx != -1:
            self.counts[idx] += 1

    def data(self) -> list[int]:
        """Returns the list of counts."""
        return self.counts

    def bins_range(self) -> list[tuple[float, float]]:
        """Returns a list of (start, end) tuples for each bin."""
        ranges = []
        for i in range(self.bins):
            start = self._get_value_at_index(i)
            end = self._get_value_at_index(i + 1)
            ranges.append((start, end))
        return ranges

    def _get_value_at_index(self, index: int) -> float:
        fraction = index / self.bins
        if self.scale == "log":
            log_min = math.log(self.min)
            log_max = math.log(self.max)
            return math.exp(log_min + fraction * (log_max - log_min))
        return self.min + fraction * (self.max - self.min)

    def _get_bin_index(self, value: float) -> int:
        if not (self.min <= value <= self.max):
            return -1
        if self.scale == "log":
            norm = (math.log(value) - math.log(self.min)) / (
                math.log(self.max) - math.log(self.min)
            )
        else:
            norm = (value - self.min) / (self.max - self.min)
        return min(int(norm * self.bins), self.bins - 1)

    def add(self, value: float):
        idx = self._get_bin_index(value)
        if idx != -1:
            self.counts[idx] += 1
