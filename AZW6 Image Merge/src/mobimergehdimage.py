#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct, os, sys
from io import BytesIO

# 使用 Calibre 內建的 Pillow 庫來替代已移除的 imghdr
try:
    from PIL import Image
except ImportError:
    Image = None

#################################################################################
#                                                                               #
#                             MOBI HDImage Merger                               #
#                                                                               #
#                       2019 Choryu Park (Kyoungkyu Park)                       #
#                                                                               #
#################################################################################

## Header offsets (保持原樣)
BHDR_OFFSET_NUM_OF_RECORD = 76
BHDR_OFFSET_FILE_IDENT = 60
BHDR_RECORD0_OFFSET_TEXT_ENCODING = 28
BHDR_RECORD0_OFFSET_FULL_NAME_OFFSET = 84
BHDR_RECORD0_OFFSET_FULL_NAME_LENGTH = 88
BHDR_RECORD0_OFFSET_FIRST_IMAGE_INDEX = 108
BHDR_OFFSET_RECORD_INFO_LIST = 78
CHDR_OFFSET_FILE_IDENT = 60
CHDR_RECORD0_OFFSET_TEXT_ENCODING = 12
CHDR_RECORD0_OFFSET_FULL_NAME_OFFSET = 40
CHDR_RECORD0_OFFSET_FULL_NAME_LENGTH = 44

TEXT_ENCODING_MAP = {65001: "UTF-8", 1252: "windows-1252"}
CONTAINER_CONTENT_TYPE_IMAGE = "IMAGE"
CONTAINER_CONTENT_TYPE_PLACEHOLDER = "PLACEHOLDER"
CONTAINER_NEEDED_TYPES = {b"CRES": CONTAINER_CONTENT_TYPE_IMAGE, b"\xa0\xa0\xa0\xa0": CONTAINER_CONTENT_TYPE_PLACEHOLDER}

def get_image_type(imgdata):
    # 優先嘗試使用 Pillow (解決 Python 3.13+ 移除 imghdr 的問題)
    if Image is not None:
        try:
            with Image.open(BytesIO(imgdata)) as img:
                imgtype = img.format.lower()
                if imgtype == "tiff":
                    return "wdp"
                return imgtype
        except:
            pass

    # 手動檢查邏輯 (備援)
    if imgdata[0:2] == b'\xFF\xD8':
        last = len(imgdata)
        while (last > 0 and imgdata[last-1:last] == b'\x00'):
            last -= 1
        if last >= 2 and imgdata[last-2:last] == b'\xFF\xD9':
            return "jpeg"
    return None

def get_charset(data, offset):
    charset_id, = struct.unpack_from(">L", data, offset)
    if charset_id in TEXT_ENCODING_MAP:
        return TEXT_ENCODING_MAP[charset_id]
    else:
        print("Unknown Charset %d" % charset_id)
        raise

def get_book_title(data, base_offset, name_offset, length_offset, charset):
    name_offset, = struct.unpack_from(">L", data, base_offset + name_offset)
    name_length, = struct.unpack_from(">L", data, base_offset + length_offset)
    name_offset += base_offset
    return data[name_offset:name_offset + name_length].decode(charset)

class MobiMergeHDImage:
    hdimage_dict = None

    def __init__(self, mobi_data):
        self.mobi = bytearray(mobi_data)
        self.record_dict = self.get_record_dict(self.mobi)
        if self.mobi[BHDR_OFFSET_FILE_IDENT:BHDR_OFFSET_FILE_IDENT+8] != b'BOOKMOBI':
            print("This eBook is not a Mobi.")
            raise
        self.charset = get_charset(self.mobi, self.record_dict[0]["OFFSET"] + BHDR_RECORD0_OFFSET_TEXT_ENCODING)
        self.book_title = get_book_title(self.mobi, self.record_dict[0]["OFFSET"], BHDR_RECORD0_OFFSET_FULL_NAME_OFFSET, BHDR_RECORD0_OFFSET_FULL_NAME_LENGTH, self.charset)

    def get_record_dict(self, data):
        current_offset = BHDR_OFFSET_NUM_OF_RECORD
        record_count, = struct.unpack_from(">H", data, current_offset)
        record_dict = dict()
        record_dict[sys.maxsize] = record_count
        for index in range(0, record_count):
            record_dict[index] = dict()
            offset = BHDR_OFFSET_RECORD_INFO_LIST + index * 8
            record_dict[index]["INFO_OFFSET"] = offset
            record_dict[index]["OFFSET"], = struct.unpack_from(">L", data, offset)
        return record_dict

    def load_azwres(self, res_file):
        with open(res_file, 'rb') as azwresfile:
            azwres = azwresfile.read()
        if azwres[CHDR_OFFSET_FILE_IDENT:CHDR_OFFSET_FILE_IDENT + 8] != b'RBINCONT':
            print("%s is not a HDImage container." % os.path.basename(res_file))
            raise
        azwres_dict = self.get_record_dict(azwres)
        azwres_title = get_book_title(azwres, azwres_dict[0]["OFFSET"], CHDR_RECORD0_OFFSET_FULL_NAME_OFFSET, CHDR_RECORD0_OFFSET_FULL_NAME_LENGTH, self.charset)
        if self.book_title != azwres_title:
            print("Book mismatch. Book title and HDImage container title is not same. ")
            print("Book: %s, Container: %s" % (self.book_title, azwres_title))
            raise
        self.hdimage_dict = dict()
        image_index = 0
        for index, val in sorted(azwres_dict.items()):
            if index != sys.maxsize and azwres[val["OFFSET"]:val["OFFSET"] + 2] != b"\xe9\x8e":
                if azwres[val["OFFSET"]:val["OFFSET"] + 4] in CONTAINER_NEEDED_TYPES:
                    self.hdimage_dict[image_index] = dict()
                    self.hdimage_dict[image_index]["INDEX"] = index
                    self.hdimage_dict[image_index]["TYPE"] = CONTAINER_NEEDED_TYPES[azwres[val["OFFSET"]:val["OFFSET"] + 4]]
                    if self.hdimage_dict[image_index]["TYPE"] == CONTAINER_CONTENT_TYPE_IMAGE:
                        self.hdimage_dict[image_index]["CONTENT"] = azwres[val["OFFSET"] + 12:azwres_dict[index + 1]["OFFSET"]]
                    image_index += 1

    def record_offset_update(self, record_index, modified_offset_size):
        for target_record_index in range(record_index + 1, self.record_dict[sys.maxsize]):
            newoffset = self.record_dict[target_record_index]["OFFSET"] + modified_offset_size
            self.record_dict[target_record_index]["OFFSET"] = newoffset
            infooffset = self.record_dict[target_record_index]["INFO_OFFSET"]           
            self.mobi[infooffset:infooffset + 4] = struct.pack(">L", newoffset)

    def merge(self):
        if self.hdimage_dict is None:
            print("'azw.res' file is not loaded yet.")
            raise
        first_record_offset = self.record_dict[0]['OFFSET']
        first_image_index, = struct.unpack_from(">L", self.mobi, first_record_offset + 108)
        images_dict = dict()
        image_index = 0
        for record_index in range(first_image_index, self.record_dict[sys.maxsize]):
            if record_index + 1 == self.record_dict[sys.maxsize]:
                img = self.mobi[self.record_dict[record_index]["OFFSET"]:]
            else:    
                img = self.mobi[self.record_dict[record_index]["OFFSET"]:self.record_dict[record_index + 1]["OFFSET"]]
            if get_image_type(img) is not None:
                images_dict[image_index] = dict()
                images_dict[image_index]["INDEX"] = record_index
                images_dict[image_index]["CONTENT"] = img
                image_index += 1
        for index, hdimage in list(self.hdimage_dict.items()):
            if hdimage["TYPE"] == CONTAINER_CONTENT_TYPE_IMAGE:
                if self.mobi.find(images_dict[index]["CONTENT"]) != -1:
                    size_difference = len(hdimage["CONTENT"]) - len(images_dict[index]["CONTENT"])
                    original_index = images_dict[index]["INDEX"]
                    if original_index + 1 == self.record_dict[sys.maxsize]:
                        self.mobi[self.record_dict[original_index]["OFFSET"]:] = hdimage["CONTENT"]
                    else:    
                        self.mobi[self.record_dict[original_index]["OFFSET"]:self.record_dict[original_index + 1]["OFFSET"]] = hdimage["CONTENT"]
                    self.record_offset_update(images_dict[index]["INDEX"], size_difference)
        return self.mobi
