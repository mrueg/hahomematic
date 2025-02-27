"""
Module for entities implemented using the switch platform.

See https://www.home-assistant.io/integrations/switch/.
"""
from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
import logging
from typing import Any, Final

from hahomematic.const import HmPlatform, Parameter
from hahomematic.platforms import device as hmd
from hahomematic.platforms.custom import definition as hmed
from hahomematic.platforms.custom.const import DeviceProfile, Field
from hahomematic.platforms.custom.entity import CustomEntity
from hahomematic.platforms.custom.support import CustomConfig, ExtendedConfig
from hahomematic.platforms.decorators import value_property
from hahomematic.platforms.entity import CallParameterCollector, bind_collector
from hahomematic.platforms.generic.action import HmAction
from hahomematic.platforms.generic.binary_sensor import HmBinarySensor
from hahomematic.platforms.generic.switch import HmSwitch
from hahomematic.platforms.support import OnTimeMixin

_LOGGER: Final = logging.getLogger(__name__)


class StateChangeArg(StrEnum):
    """Enum with switch state change arguments."""

    OFF = "off"
    ON = "on"
    ON_TIME = "on_time"


class CeSwitch(CustomEntity, OnTimeMixin):
    """Class for HomeMatic switch entities."""

    _platform = HmPlatform.SWITCH

    def _init_entity_fields(self) -> None:
        """Init the entity fields."""
        OnTimeMixin.__init__(self)
        super()._init_entity_fields()
        self._e_state: HmSwitch = self._get_entity(field=Field.STATE, entity_type=HmSwitch)
        self._e_on_time_value: HmAction = self._get_entity(
            field=Field.ON_TIME_VALUE, entity_type=HmAction
        )
        self._e_channel_state: HmBinarySensor = self._get_entity(
            field=Field.CHANNEL_STATE, entity_type=HmBinarySensor
        )

    @value_property
    def channel_value(self) -> bool | None:
        """Return the current channel value of the switch."""
        return self._e_channel_state.value

    @value_property
    def value(self) -> bool | None:
        """Return the current value of the switch."""
        return self._e_state.value

    @bind_collector
    async def turn_on(
        self, collector: CallParameterCollector | None = None, on_time: float | None = None
    ) -> None:
        """Turn the switch on."""
        if not self.is_state_change(on=True, on_time=on_time):
            return
        if on_time is not None or (on_time := self.get_on_time_and_cleanup()):
            await self._e_on_time_value.send_value(value=float(on_time), collector=collector)
        await self._e_state.turn_on(collector=collector)

    @bind_collector
    async def turn_off(self, collector: CallParameterCollector | None = None) -> None:
        """Turn the switch off."""
        if not self.is_state_change(off=True):
            return
        await self._e_state.turn_off(collector=collector)

    def is_state_change(self, **kwargs: Any) -> bool:
        """Check if the state changes due to kwargs."""
        if kwargs.get(StateChangeArg.ON_TIME) is not None:
            return True
        if kwargs.get(StateChangeArg.ON) is not None and self.value is not True:
            return True
        if kwargs.get(StateChangeArg.OFF) is not None and self.value is not False:
            return True
        return super().is_state_change(**kwargs)


def make_ip_switch(
    device: hmd.HmDevice,
    group_base_channels: tuple[int, ...],
    extended: ExtendedConfig | None = None,
) -> tuple[CustomEntity, ...]:
    """Create HomematicIP switch entities."""
    return hmed.make_custom_entity(
        device=device,
        entity_class=CeSwitch,
        device_profile=DeviceProfile.IP_SWITCH,
        group_base_channels=group_base_channels,
        extended=extended,
    )


# Case for device model is not relevant.
# HomeBrew (HB-) devices are always listed as HM-.
DEVICES: Mapping[str, CustomConfig | tuple[CustomConfig, ...]] = {
    "ELV-SH-BS2": CustomConfig(func=make_ip_switch, channels=(3, 7)),
    "HmIP-BS2": CustomConfig(func=make_ip_switch, channels=(3, 7)),
    "HmIP-BSL": CustomConfig(func=make_ip_switch, channels=(3,)),
    "HmIP-BSM": CustomConfig(func=make_ip_switch, channels=(3,)),
    "HmIP-DRSI1": CustomConfig(
        func=make_ip_switch,
        channels=(2,),
        extended=ExtendedConfig(
            additional_entities={
                0: (Parameter.ACTUAL_TEMPERATURE,),
            }
        ),
    ),
    "HmIP-DRSI4": CustomConfig(
        func=make_ip_switch,
        channels=(5, 9, 13, 17),
        extended=ExtendedConfig(
            additional_entities={
                0: (Parameter.ACTUAL_TEMPERATURE,),
            }
        ),
    ),
    "HmIP-FSI": CustomConfig(func=make_ip_switch, channels=(2,)),
    "HmIP-FSM": CustomConfig(func=make_ip_switch, channels=(1,)),
    "HmIP-MOD-OC8": CustomConfig(func=make_ip_switch, channels=(9, 13, 17, 21, 25, 29, 33, 37)),
    "HmIP-PCBS": CustomConfig(func=make_ip_switch, channels=(2,)),
    "HmIP-PCBS-BAT": CustomConfig(func=make_ip_switch, channels=(2,)),
    "HmIP-PCBS2": CustomConfig(func=make_ip_switch, channels=(3, 7)),
    "HmIP-PS": CustomConfig(func=make_ip_switch, channels=(2,)),
    "HmIP-SCTH230": CustomConfig(func=make_ip_switch, channels=(7,)),
    "HmIP-USBSM": CustomConfig(func=make_ip_switch, channels=(2,)),
    "HmIP-WGC": CustomConfig(func=make_ip_switch, channels=(2,)),
    "HmIP-WHS2": CustomConfig(func=make_ip_switch, channels=(1, 5)),
    "HmIPW-DRS": CustomConfig(
        func=make_ip_switch,
        channels=(1, 5, 9, 13, 17, 21, 25, 29),
        extended=ExtendedConfig(
            additional_entities={
                0: (Parameter.ACTUAL_TEMPERATURE,),
            }
        ),
    ),
    "HmIPW-FIO6": CustomConfig(func=make_ip_switch, channels=(7, 11, 15, 19, 23, 27)),
}
hmed.ALL_DEVICES.append(DEVICES)
