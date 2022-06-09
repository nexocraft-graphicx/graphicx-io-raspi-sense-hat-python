#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .proto import tsbatch_pb2
import copy
import datetime
import enum
import mimetypes
import orjson
import typing


class Timeseries:
    class InvalidTimestampError(Exception):
        pass

    class InvalidDataType(Exception):
        pass

    class InvalidAttributeError(Exception):
        pass

    class InvalidStateError(Exception):
        pass

    @enum.unique
    class DataType(enum.IntEnum):
        NUMERIC = tsbatch_pb2.DataType.NUMERIC
        STRING = tsbatch_pb2.DataType.STRING
        JSON = tsbatch_pb2.DataType.JSON
        BINARY = tsbatch_pb2.DataType.BINARY

    @enum.unique
    class DuplicateTimestampStrategy(enum.IntEnum):
        RAISE = 0
        IGNORE = 1
        OVERWRITE = 2

    ValueType = typing.Union[str, float, int, bytes]

    def __init__(
        self,
        *args,
        data_type: DataType,
        group: typing.Optional[str],
        source: str,
        mime_type: typing.Optional[str] = None,
        unit: typing.Optional[int] = None,
        name: typing.Optional[str] = None,
        duplicate_timestamp_strategy: DuplicateTimestampStrategy = DuplicateTimestampStrategy.RAISE,
    ):

        self.__data_type = Timeseries.DataType(data_type)
        self.__duplicate_timestamp_strategy = Timeseries.DuplicateTimestampStrategy(duplicate_timestamp_strategy)


        if not source:
            raise Timeseries.InvalidAttributeError("timeseries 'source' attribute cannot be empty")

        group_and_source = Timeseries.normalize_group_and_source(group=group, source=source)
        self.__group = group_and_source[0]
        self.__source = group_and_source[1]

        self.__mime_type = None
        if self.__data_type == Timeseries.DataType.BINARY:
            if mime_type is None:
                raise Timeseries.InvalidAttributeError(
                    "unable to initialize Timeseries with data type BINARY without mime type"
                )

            # use mime_types_db.add_type or mime_types_db.read to add additional,
            # potentially custom types if they happen to be missing from the default db
            mime_types_db = mimetypes.MimeTypes(strict=True)
            mime_types_db.add_type("application/octet-stream", ".bin", strict=False)

            self.__mime_type = mime_type.strip().lower()
            if (
                self.__mime_type not in mime_types_db.types_map_inv[0]
                and self.__mime_type not in mime_types_db.types_map_inv[1]
            ):
                raise Timeseries.InvalidAttributeError(f"unknown mime type '{self.__mime_type}")

        self.__timestamps = {}
        self.__read_only = False
        self.__values = []
        self.__unit_id = None if unit is None or unit == -1 else int(unit)
        self.__name = name.strip() if name else None

    @classmethod
    def normalize_group_and_source(cls, *args, group: typing.Optional[str], source: str) -> typing.Tuple[typing.Optional[str], str]:
        return (
            None if not group else group.strip(),
            source.strip()
        )

    @property
    def group(self) -> str:
        return self.__group

    @property
    def source(self) -> str:
        return self.__source

    @property
    def data_type(self) -> DataType:
        return self.__data_type

    @property
    def mime_type(self) -> str:
        return self.__mime_type

    @property
    def values(self) -> typing.List[typing.Tuple[datetime.datetime, ValueType]]:
        return copy.deepcopy(self.__values)

    @property
    def unit(self) -> typing.Optional[int]:
        # a unit id according to the UNECE "Codes for Units of Measure Used in International Trade" recommendation 20
        # https://tfig.unece.org/contents/recommendation-20.htm
        # we use the mapping of UNECE units to OPC UA unit ids available here:
        # http://www.opcfoundation.org/UA/EngineeringUnits/UNECE/UNECE_to_OPCUA.csv
        # This mapping can obviously also be used to Timeseries created from sources other than OPC UA
        return self.__unit_id

    @property
    def name(self) -> typing.Optional[str]:
        return self.__name

    @property
    def read_only(self) -> bool:
        return self.__read_only

    @property
    def duplicate_timestamp_strategy(self) -> DuplicateTimestampStrategy:
        return self.__duplicate_timestamp_strategy

    @staticmethod
    def check_timestamp(timestamp: datetime.datetime):
        if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
            raise Timeseries.InvalidTimestampError("timestamps without time zone information are not supported")
        if timestamp.tzname() != "UTC":
            raise Timeseries.InvalidTimestampError("only UTC timestamps are supported")

    def __check_data_type(self, value: ValueType) -> typing.Union[float, str, bytes]:
        try:
            if self.__data_type == Timeseries.DataType.NUMERIC:
                return float(value)
            elif self.__data_type == Timeseries.DataType.STRING:
                # almost everything can be converted to a string, so we will be a bit
                # more explicit here, requiring that the user has already ensured they
                # pass a str to us so that they are at least aware of what they're doing
                if not isinstance(value, str):
                    raise ValueError("will not implicitly convert value to string")
                return str(value)
            elif self.__data_type == Timeseries.DataType.JSON:
                return orjson.dumps(value)
            elif self.__data_type == Timeseries.DataType.BINARY:
                return bytes(value)
            else:
                # this will only happen if somebody added a new data type, but did not update the implementation
                raise NotImplementedError(f"unknown data type '{self.__data_type}'")
        except Exception as e:
            raise Timeseries.InvalidDataType(
                f"timeseries has data type {self.__data_type}, cannot accept value '{value}'"
            ) from e

    def add_value(self, *args, timestamp: datetime.datetime, value: ValueType):

        if self.__read_only:
            raise Timeseries.InvalidStateError("this timeseries is read-only and cannot accept new values")

        Timeseries.check_timestamp(timestamp)

        value = self.__check_data_type(value)

        if timestamp in self.__timestamps:
            if self.__duplicate_timestamp_strategy == Timeseries.DuplicateTimestampStrategy.RAISE:
                raise Timeseries.InvalidTimestampError(f"a value for timestamp {timestamp} has already been added")
            elif self.__duplicate_timestamp_strategy == Timeseries.DuplicateTimestampStrategy.IGNORE:
                return
            elif self.__duplicate_timestamp_strategy == Timeseries.DuplicateTimestampStrategy.OVERWRITE:
                value_index = self.__timestamps[timestamp]
                self.__values[value_index] = (timestamp, value)
        else:
            self.__timestamps[timestamp] = len(self.__timestamps)
            self.__values.append((timestamp, value))

    def serialize_to(self, protobuf_ts: tsbatch_pb2.Timeseries):
        if protobuf_ts is None:
            raise Timeseries.InvalidStateError("serialization requires a protobuf Timeseries destination object")

        if self.__data_type == Timeseries.DataType.NUMERIC:
            field = protobuf_ts.v_numeric
        elif self.__data_type == Timeseries.DataType.STRING:
            field = protobuf_ts.v_string
        elif self.__data_type == Timeseries.DataType.JSON:
            field = protobuf_ts.v_json
        elif self.__data_type == Timeseries.DataType.BINARY:
            field = protobuf_ts.v_binary
        else:
            # this will only happen if somebody added a new data type, but did not update the implementation
            raise NotImplementedError(f"serialization for data type '{self.__data_type}' not implemented")

        if len(field.values) > 0:
            raise Timeseries.InvalidStateError("cannot add values to an already existing timeseries")

        protobuf_ts.duplicateTimestampStrategy = self.__duplicate_timestamp_strategy
        protobuf_ts.source = self.__source
        if self.__group is not None:
            protobuf_ts.group = self.__group
        protobuf_ts.dataType = self.__data_type.value
        if self.__name:
            protobuf_ts.name = self.__name
        if self.__unit_id:
            protobuf_ts.unit = self.__unit_id

        if self.__mime_type is not None:
            protobuf_ts.mimeType = self.__mime_type

        for timestamp, value in self.__values:
            entry = field.values.add()
            entry.timestamp.FromDatetime(timestamp)
            entry.value = value

        self.__read_only = True
