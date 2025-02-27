"""Tests for number entities of hahomematic."""
from __future__ import annotations

from typing import cast
from unittest.mock import call

import pytest

from hahomematic.const import EntityUsage
from hahomematic.platforms.generic.number import HmFloat, HmInteger
from hahomematic.platforms.hub.number import HmSysvarNumber

from tests import const, helper

TEST_DEVICES: dict[str, str] = {
    "VCU4984404": "HmIPW-STHD.json",
    "VCU0000011": "HMW-LC-Bl1-DR.json",
    "VCU0000054": "HM-CC-TC.json",
}

# pylint: disable=protected-access


@pytest.mark.asyncio
async def test_hmfloat(factory: helper.Factory) -> None:
    """Test HmFloat."""
    central, mock_client = await factory.get_default_central(TEST_DEVICES)
    efloat: HmFloat = cast(
        HmFloat,
        central.get_generic_entity("VCU0000011:3", "LEVEL"),
    )
    assert efloat.usage == EntityUsage.NO_CREATE
    assert efloat.unit == "%"
    assert efloat.values is None
    assert efloat.value is None
    await efloat.send_value(0.3)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000011:3",
        paramset_key="VALUES",
        parameter="LEVEL",
        value=0.3,
    )
    assert efloat.value == 0.3
    central.event(const.INTERFACE_ID, "VCU0000011:3", "LEVEL", 0.5)
    assert efloat.value == 0.5
    # do not write. value above max
    await efloat.send_value(45.0)
    assert efloat.value == 0.5

    call_count = len(mock_client.method_calls)
    await efloat.send_value(45.0)
    assert call_count == len(mock_client.method_calls)


@pytest.mark.asyncio
async def test_hmfloat_special(factory: helper.Factory) -> None:
    """Test HmFloat."""
    central, mock_client = await factory.get_default_central(TEST_DEVICES)
    efloat: HmFloat = cast(
        HmFloat,
        central.get_generic_entity("VCU0000054:2", "SETPOINT"),
    )
    assert efloat.usage == EntityUsage.NO_CREATE
    assert efloat.unit == "°C"
    assert efloat.values is None
    assert efloat.value is None
    await efloat.send_value(8.0)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000054:2",
        paramset_key="VALUES",
        parameter="SETPOINT",
        value=8.0,
    )
    assert efloat.value == 8.0

    await efloat.send_value("VENT_OPEN")
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000054:2",
        paramset_key="VALUES",
        parameter="SETPOINT",
        value=100.0,
    )
    assert efloat.value == 100.0


@pytest.mark.asyncio
async def test_hminteger(factory: helper.Factory) -> None:
    """Test HmInteger."""
    central, mock_client = await factory.get_default_central(TEST_DEVICES)
    einteger: HmInteger = cast(
        HmInteger,
        central.get_generic_entity("VCU4984404:1", "SET_POINT_MODE"),
    )
    assert einteger.usage == EntityUsage.NO_CREATE
    assert einteger.unit is None
    assert einteger.min == 0
    assert einteger.max == 3
    assert einteger.values is None
    assert einteger.value is None
    await einteger.send_value(3)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU4984404:1",
        paramset_key="VALUES",
        parameter="SET_POINT_MODE",
        value=3,
    )
    assert einteger.value == 3
    central.event(const.INTERFACE_ID, "VCU4984404:1", "SET_POINT_MODE", 2)
    assert einteger.value == 2
    await einteger.send_value(6)
    assert mock_client.method_calls[-1] != call.set_value(
        channel_address="VCU4984404:1",
        paramset_key="VALUES",
        parameter="SET_POINT_MODE",
        value=6,
    )
    # do not write. value above max
    assert einteger.value == 2

    call_count = len(mock_client.method_calls)
    await einteger.send_value(6)
    assert call_count == len(mock_client.method_calls)


@pytest.mark.asyncio
async def test_hmsysvarnumber(factory: helper.Factory) -> None:
    """Test HmSysvarNumber."""
    central, mock_client = await factory.get_default_central({}, add_sysvars=True)
    enumber: HmSysvarNumber = cast(
        HmSysvarNumber,
        central.get_sysvar_entity("sv_float_ext"),
    )
    assert enumber.usage == EntityUsage.ENTITY
    assert enumber.unit == "°C"
    assert enumber.min == 5.0
    assert enumber.max == 30.0
    assert enumber.values is None
    assert enumber.value == 23.2

    await enumber.send_variable(23.0)
    assert mock_client.method_calls[-1] == call.set_system_variable(
        name="sv_float_ext", value=23.0
    )
    assert enumber.value == 23.0

    await enumber.send_variable(35.0)
    # value over max won't change value
    assert enumber.value == 23.0
