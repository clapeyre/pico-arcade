# https://www.displayfuture.com/Display/datasheet/controller/SH1107.pdf

from micropython import const
from framebuf import FrameBuffer, MONO_VLSB, MONO_HMSB
from machine import Pin, I2C
from lib.tools import singleton
from drivers.i2c import I2C0

SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_DCDC_MODE = const(0xAD)
SET_MEM_MODE = const(0x20)
SET_PAGE_ADDR = const(0xB0)
SET_COL_LO_ADDR = const(0x00)
SET_COL_HI_ADDR = const(0x10)
SET_DISP_START_LINE = const(0xDC)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)

TEST_CHUNK = const(8)


class SH1107(FrameBuffer):
    # A monochrome approach should be used for coding this. The rgb method ensures
    # nothing breaks if users specify colors.
    @staticmethod
    def rgb(r, g, b):
        return int(((r | g | b) & 0x80) > 0)

    def __init__(self, width, height, external_vcc):
        self.external_vcc = external_vcc
        if width == 128 and height == 64:
            self.page_mode = False
        elif (width == 64 and height == 128) or (width == 128 and height == 128):
            self.page_mode = True
        else:
            raise ValueError
        self.width = width
        self.height = height
        self.pages = self.height // 8
        self.line_bytes = self.width // 8
        size = self.width * self.height // 8
        self.curr_buffer = bytearray(b"\x00" * size)  # self.fill(0)
        self.prev_buffer = bytearray(b"\xff" * size)  # force full refresh
        super().__init__(
            self.curr_buffer,
            self.width,
            self.height,
            MONO_VLSB if self.page_mode else MONO_HMSB,
        )
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP |           0x00, # off
            # address setting
            SET_MEM_MODE |       (0x00 if self.page_mode else 0x01), # 0x00 = page, 0x01 = vertical
            # resolution and layout
            SET_DISP_START_LINE, 0x00,
            SET_SEG_REMAP |      0x00, # 0x01 rotate 180 deg
            SET_COM_OUT_DIR |    (0x00 if self.page_mode else 0x08), # 0x08 rotate 180 deg
            SET_MUX_RATIO,       0x7f, # always this?
            SET_DISP_OFFSET,     0x60 if self.width != self.height else 0x00, # offseted for 64 x 128 (Aliexpress 0.96")
            # timing and driving scheme
            SET_DISP_CLK_DIV,    0x50,
            SET_PRECHARGE,       0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL,      0x35, # 0.77 * Vcc
            SET_DCDC_MODE,       0x81, # on, 0.6 * switch freq
            # display
            SET_CONTRAST,        0x10, # very low to avoid uneven background
            SET_ENTIRE_ON |      0x00, # output follows RAM contents, not entire on
            SET_NORM_INV |       0x00  # 0x00 = not inverted, 0x01 = inverted
        ):
            self.write_cmd(cmd)
        # buffers are initialized as if self.fill(0) was called
        self.show()
        self.poweron()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        if self.page_mode:
            self.show_page_mode()
        else:
            self.show_vert_mode()
        self.prev_buffer[:] = self.curr_buffer

    def show_page_mode(self):
        for page in range(self.pages):
            noffs = page * self.width
            for col1, col2 in self.test_modified(noffs, self.width):
                c = col1 - noffs
                self.write_cmd(SET_PAGE_ADDR | page)
                self.write_cmd(SET_COL_LO_ADDR | (c & 0x0f))
                self.write_cmd(SET_COL_HI_ADDR | ((c & 0x70) >> 4))
                self.write_data(self.curr_buffer[col1:col2])
                # print('Write offsets {} : {}, col: {}'.format(col1, col2, c))

    def show_vert_mode(self):
        for col in range(self.height):
            noffs = col * self.line_bytes
            for page1, page2 in self.test_modified(noffs, self.line_bytes):
                self.write_cmd(SET_PAGE_ADDR | (page1 - noffs))
                self.write_cmd(SET_COL_LO_ADDR | (col & 0x0f))
                self.write_cmd(SET_COL_HI_ADDR | ((col & 0x70) >> 4))
                self.write_data(self.curr_buffer[page1:page2])
                # print('Write offsets {} : {}, page: {}'.format(page1, page2, page1 - noffs))

    def test_modified(self, offs, width):
        ptr = offs
        width += offs
        while ptr < width:
            # skip unmodified chunks
            while (
                ptr < width
                and self.curr_buffer[ptr : ptr + TEST_CHUNK]
                == self.prev_buffer[ptr : ptr + TEST_CHUNK]
            ):
                ptr += TEST_CHUNK

            if ptr < width:
                first = ptr
                ptr += TEST_CHUNK
                # find modified chunks
                while (
                    ptr < width
                    and self.curr_buffer[ptr : ptr + TEST_CHUNK]
                    != self.prev_buffer[ptr : ptr + TEST_CHUNK]
                ):
                    ptr += TEST_CHUNK

                yield first, ptr
                ptr += TEST_CHUNK

    def text_wrap(self, txt, start=0, strict=False):
        wrapped = [txt.split()[0]]
        for word in txt.split()[1:]:
            if len(wrapped[-1]) + len(word) + 1 > 15:
                wrapped.append(word)
            else:
                wrapped[-1] += " " + word
        if strict:
            if len(wrapped) > 7 - start:
                raise ValueError("Text doesn't fit, need taller screen")
            if any(len(line) > 15 for line in wrapped):
                raise ValueError("Text doesn't fit, need wider screen")
        for line in wrapped:
            self.text(line, 0, start * 10, 1)
            start += 1


class DummyDisplay:
    """Fallback display that does nothing when real display is unavailable"""

    def __init__(self, *args, **kwargs):
        print("Using dummy display (no actual display connected)")

    def fill(self, *args):
        pass

    def text(self, *args, **kwargs):
        pass

    def show(self):
        pass

    def text_wrap(self, *args, **kwargs):
        pass


@singleton
class SH1107_I2C(SH1107):
    def __init__(self, width=128, height=64, addr=0x3C, external_vcc=False):
        self.i2c = I2C0
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        self.error = None
        try:
            super().__init__(width, height, external_vcc)
        except Exception as e:
            print(f"Warning: Failed to initialize display: {e}")
            self.error = e
            # Create dummy methods for graceful degradation
            self.fill = lambda *args: None
            self.text = lambda *args: None
            self.show = lambda *args: None
            self.text_wrap = lambda *args: None

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        try:
            self.i2c.writeto(self.addr, self.temp)
        except OSError as e:
            if self.error is None:
                print(f"Couldn't write to I2C addr {hex(self.addr)}")
                print(e)
                self.error = e

    def write_data(self, buf):
        self.write_list[1] = buf
        try:
            self.i2c.writevto(self.addr, self.write_list)
        except OSError as e:
            if self.error is None:
                print(f"Couldn't write to I2C addr {hex(self.addr)}")
                print(e)
                self.error = e
