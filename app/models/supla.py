from pydantic import BaseModel


class ChannelType(BaseModel):
    id: int
    name: str
    caption: str


class ChannelFunction(BaseModel):
    id: int
    name: str
    caption: str


class PossibleAction(BaseModel):
    id: int
    name: str
    nameSlug: str
    caption: str


class GateConfig(BaseModel):
    openingSensorChannelId: int | None = None
    relayTimeMs: int | None = None
    numberOfAttemptsToOpen: int | None = None
    numberOfAttemptsToClose: int | None = None


class GateChannel(BaseModel):
    id: int
    caption: str | None

    iodeviceId: int
    locationId: int

    functionId: int
    typeId: int

    type: ChannelType
    function: ChannelFunction

    possibleActions: list[PossibleAction]

    config: GateConfig

    @property
    def sensor_channel_id(self) -> int | None:
        return self.config.openingSensorChannelId

    @property
    def action_names(self) -> list[str]:
        return [action.name for action in self.possibleActions]
