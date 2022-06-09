#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .proto import tsbatch_pb2
from .timeseries import Timeseries
import contextlib
import hashlib
import typing
import zstandard


class Batch:
    class DuplicateTimeseriesError(Exception):
        pass

    class InvalidStateError(Exception):
        pass

    def __init__(self):
        self.__timeseries = {}
        self.__message = None

    def add_timeseries(
        self,
        *args,
        data_type: Timeseries.DataType,
        group: typing.Optional[str],
        source: str,
        mime_type: typing.Optional[str] = None,
        unit: typing.Optional[int] = None,
        name: typing.Optional[str] = None,
        duplicate_timestamp_strategy: Timeseries.DuplicateTimestampStrategy = Timeseries.DuplicateTimestampStrategy.RAISE,
    ) -> Timeseries:

        if self.__message is not None:
            raise Batch.InvalidStateError("unable to add additional timeseries: this batch has already been serialized")

        group_and_source = Timeseries.normalize_group_and_source(group=group, source=source)
        if group_and_source in self.__timeseries:
            raise Batch.DuplicateTimeseriesError(
                f"a timeseries with {{'group': {group}, 'source' :{source}}} already exists in this batch"
            )

        ts = Timeseries(
            name=name,
            unit=unit,
            data_type=data_type,
            group=group,
            source=source,
            mime_type=mime_type,
            duplicate_timestamp_strategy=duplicate_timestamp_strategy,
        )
        assert (ts.group, ts.source) == group_and_source
        self.__timeseries[group_and_source] = ts
        return ts

    @property
    def message(self) -> bytes:
        if self.__message is None:
            raise Batch.InvalidStateError(
                "unable to serialize batch: batch is empty, or an exception occured during batch composition"
            )
        return self.__message

    def __serialize(self) -> bytes:
        batch = tsbatch_pb2.Batch()
        for timeseries in self.__timeseries.values():
            protobuf_ts = batch.timeseries.add()
            timeseries.serialize_to(protobuf_ts=protobuf_ts)

        frame = tsbatch_pb2.Frame()
        frame.contentType = tsbatch_pb2.Frame.ContentType.ZSTD_COMPRESSED_BATCH
        # level 14 has been empirically determined as the threshold for dimnishing returns
        content = zstandard.compress(batch.SerializeToString(), level=14)
        h = hashlib.sha3_512()
        h.update(content)
        frame.content = content
        frame.messageId = h.hexdigest()
        self.__message = frame.SerializeToString()


@contextlib.contextmanager
def compose_batch() -> Batch:
    batch = Batch()
    yield batch
    batch._Batch__serialize()
