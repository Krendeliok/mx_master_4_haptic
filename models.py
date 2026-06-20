from pydantic import BaseModel, computed_field, Field, field_validator

DEFAULT_BUTTON_STYLE = """
	QPushButton {
		border-radius: 36px;
		background-color: rgba(40, 40, 40, 230);
		color: white;
		font-size: 22px;
		font-weight: bold;
		border: 2px solid rgba(255, 255, 255, 80);
	}
	QPushButton:hover {
		background-color: rgba(90, 90, 90, 240);
	}
"""


class ButtonConfigModel(BaseModel):
    label: str
    action: dict | str


def _default_buttons() -> list[ButtonConfigModel]:
    return [
        ButtonConfigModel(label="Default", action=""),
        ButtonConfigModel(label="Default", action=""),
    ]


class ConfigModel(BaseModel):
    radius: int = 120
    button_size: int = 72
    drag_threshold: int = 8
    dead_zone: int = 24
    button_style: str = DEFAULT_BUTTON_STYLE
    buttons: list[ButtonConfigModel] = Field(default_factory=_default_buttons)

    @field_validator("buttons")
    @classmethod
    def validate_buttons(cls, v):
        if len(v) < 1:
            return _default_buttons()
        return v

    @computed_field
    @property
    def buttons_amount(self) -> int:
        return len(self.buttons)
