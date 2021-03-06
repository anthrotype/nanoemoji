# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helpers for expressing paint.

Based on https://github.com/googlefonts/colr-gradients-spec/blob/master/colr-gradients-spec.md#structure-of-gradient-colr-v1-extensions.
"""
import dataclasses
from enum import Enum
from nanoemoji.colors import Color, css_color
from nanosvg.geometric_types import Point
from typing import ClassVar, Tuple


class Extend(Enum):
    PAD = (0,)
    REPEAT = (1,)
    REFLECT = (2,)


@dataclasses.dataclass(frozen=True)
class ColorStop:
    stopOffset: float = 0.0
    color: Color = css_color("black")


@dataclasses.dataclass(frozen=True)
class PaintSolid:
    format: ClassVar[int] = 1
    color: Color = css_color("black")

    def colors(self):
        yield self.color

    def to_ufo_paint(self, colors):
        return {
            "format": self.format,
            "paletteIndex": colors.index(self.color.opaque()),
            "transparency": 1.0 - self.color.alpha,
        }


def _ufoColorLine(gradient, colors):
    return {
        "stops": [
            {
                "offset": stop.stopOffset,
                "paletteIndex": colors.index(stop.color.opaque()),
                "transparency": 1.0 - stop.color.alpha,
            }
            for stop in gradient.stops
        ],
        "extend": gradient.extend.name.lower(),
    }


@dataclasses.dataclass(frozen=True)
class PaintLinearGradient:
    format: ClassVar[int] = 2
    extend: Extend = Extend.PAD
    stops: Tuple[ColorStop, ...] = dataclasses.field(default_factory=lambda: ())
    p0: Point = Point()
    p1: Point = Point()
    p2: Point = None

    def colors(self):
        for stop in self.stops:
            yield stop.color

    def to_ufo_paint(self, colors):
        result = {
            "format": self.format,
            "colorLine": _ufoColorLine(self, colors),
            "p0": self.p0,
            "p1": self.p1,
        }
        if self.p2:
            result["p2"] = self.p2
        return result


@dataclasses.dataclass(frozen=True)
class PaintRadialGradient:
    format: ClassVar[int] = 3
    extend: Extend = Extend.PAD
    stops: Tuple[ColorStop] = dataclasses.field(default_factory=lambda: ())
    c0: Point = Point()
    c1: Point = Point()
    r0: float = 0.0
    r1: float = 0.0
    # TODO Affine2x2

    def colors(self):
        for stop in self.stops:
            yield stop.color

    def to_ufo_paint(self, colors):
        result = {
            "format": self.format,
            "colorLine": _ufoColorLine(self, colors),
            "c0": self.c0,
            "c1": self.c1,
            "r0": self.r0,
            "r1": self.r1,
        }
        return result
