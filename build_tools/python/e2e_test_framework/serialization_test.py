## Copyright 2022 The IREE Authors
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from dataclasses import dataclass
from typing import List, Optional
import json
import pathlib
import collections
import enum
import typing
import unittest

from e2e_test_framework import serialization


class EnumX(enum.Enum):
  OPTION_A = "a"
  OPTION_B = "b"
  OPTION_C = "c"


@serialization.serializable
@dataclass
class TestC(object):
  float_val: float


@serialization.serializable(type_key="test_b", id_field="key")
@dataclass
class TestB(object):
  key: str
  int_val: int


@serialization.serializable
@dataclass
class TestA(object):
  b_list: List[TestB]
  c_obj: TestC
  str_val: Optional[str]
  enum_val: EnumX


@serialization.serializable
@dataclass
class TestUnsupported(object):
  path: pathlib.PurePath


@serialization.serializable(type_key="test_circular")
@dataclass
class TestCircularReference(object):
  id: str
  child: Optional["TestCircularReference"]


class SerializationTest(unittest.TestCase):

  def test_serialize_and_pack(self):
    b_obj_a = TestB(key="id_a", int_val=10)
    b_obj_b = TestB(key="id_b", int_val=20)
    test_objs = [
        TestA(b_list=[b_obj_a, b_obj_b],
              c_obj=TestC(float_val=0.1),
              str_val="test1",
              enum_val=EnumX.OPTION_B),
        TestA(b_list=[b_obj_a],
              c_obj=TestC(float_val=0.2),
              str_val=None,
              enum_val=EnumX.OPTION_C)
    ]

    results = serialization.serialize_and_pack(
        test_objs,
        root_obj_field_name="main_obj",
        keyed_obj_map_field_name="obj_map")

    self.maxDiff = None
    self.assertEqual(
        results, {
            "main_obj": [
                collections.OrderedDict(
                    b_list=["id_a", "id_b"],
                    c_obj=collections.OrderedDict(float_val=0.1),
                    str_val="test1",
                    enum_val="OPTION_B"),
                collections.OrderedDict(
                    b_list=["id_a"],
                    c_obj=collections.OrderedDict(float_val=0.2),
                    str_val=None,
                    enum_val="OPTION_C")
            ],
            "obj_map":
                collections.OrderedDict({
                    "test_b:id_a":
                        collections.OrderedDict(key="id_a", int_val=10),
                    "test_b:id_b":
                        collections.OrderedDict(key="id_b", int_val=20)
                })
        })

  def test_serialize_and_pack_with_unsupported_type(self):
    self.assertRaises(
        ValueError, lambda: serialization.serialize_and_pack(
            TestUnsupported(path=pathlib.PurePath("abc"))))

  def test_serialize_and_pack_with_unsupported_dict_key(self):
    self.assertRaises(
        ValueError, lambda: serialization.serialize_and_pack(
            collections.OrderedDict({(0, 0): "test"})))

  def test_serialize_and_pack_with_circular_reference(self):
    obj_a = TestCircularReference(id="0", child=None)
    obj_b = TestCircularReference(id="1", child=obj_a)
    obj_a.child = obj_b

    self.assertRaises(ValueError,
                      lambda: serialization.serialize_and_pack(obj_a))

  def test_roundtrip(self):
    b_obj_a = TestB(key="id_a", int_val=10)
    b_obj_b = TestB(key="id_b", int_val=20)
    test_objs = [
        TestA(b_list=[b_obj_a, b_obj_b],
              c_obj=TestC(float_val=0.1),
              str_val="test1",
              enum_val=EnumX.OPTION_B),
        TestA(b_list=[b_obj_a],
              c_obj=TestC(float_val=0.2),
              str_val=None,
              enum_val=EnumX.OPTION_C),
        TestA(b_list=[b_obj_b],
              c_obj=TestC(float_val=0.3),
              str_val="test3",
              enum_val=EnumX.OPTION_A),
    ]

    results = serialization.unpack_and_deserialize(
        serialization.serialize_and_pack(test_objs), typing.List[TestA])

    self.assertEqual(results, test_objs)

  def test_roundtrip_with_json(self):
    b_obj_a = TestB(key="id_a", int_val=10)
    b_obj_b = TestB(key="id_b", int_val=20)

    objs = collections.OrderedDict(
        x=b_obj_a,
        y=b_obj_b,
    )

    json_str = json.dumps(serialization.serialize_and_pack(objs))
    results = serialization.unpack_and_deserialize(
        json.loads(json_str), typing.OrderedDict[str, TestB])

    self.assertEqual(results, objs)


if __name__ == "__main__":
  unittest.main()
