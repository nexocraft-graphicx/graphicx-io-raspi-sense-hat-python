#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..proto import tsbatch_pb2
from ..timeseries import Timeseries
import pendulum
import typing
import zstandard


def deserialize_batch(message: bytes) -> typing.List[Timeseries]:
    if not message:
        raise ValueError("unable to deserialize empty message")

    try:
        frame = tsbatch_pb2.Frame()
        frame.ParseFromString(message)
    except Exception as e:
        raise ValueError("message does not contain a valid message frame") from e

    if frame.contentType != tsbatch_pb2.Frame.ContentType.ZSTD_COMPRESSED_BATCH:
        raise NotImplementedError("unable to deserialize message: unknown content type")

    try:
        raw_batch_message = zstandard.decompress(frame.content)
        batch = tsbatch_pb2.Batch()
        batch.ParseFromString(raw_batch_message)
    except Exception as e:
        raise ValueError("unable to deserialize unknown batch contents") from e

    timeseries = []
    for protobuf_ts in batch.timeseries:
        ts = Timeseries(
            group=protobuf_ts.group,
            source=protobuf_ts.source,
            data_type=protobuf_ts.dataType,
            mime_type=protobuf_ts.mimeType,
            duplicate_timestamp_strategy=protobuf_ts.duplicateTimestampStrategy,
        )

        if ts.data_type == Timeseries.DataType.NUMERIC:
            field = protobuf_ts.v_numeric
        elif ts.data_type == Timeseries.DataType.STRING:
            field = protobuf_ts.v_string
        elif ts.data_type == Timeseries.DataType.JSON:
            field = protobuf_ts.v_json
        elif ts.data_type == Timeseries.DataType.BINARY:
            field = protobuf_ts.v_binary

        for v in field.values:
            dt = pendulum.parse(v.timestamp.ToJsonString())
            ts.add_value(timestamp=dt, value=v.value)

        timeseries.append(ts)

    return timeseries
