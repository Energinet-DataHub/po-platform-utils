from datetime import datetime
from dataclasses import dataclass

from energytt_platform.serialize import Serializable
from energytt_platform.models.measurements import Measurement


@dataclass
class PublishMeasurement(Serializable):
    """
    A request to publish a new Measurement.
    """
    gsrn: str
    amount: int
    begin: datetime
    end: datetime


@dataclass
class NewMeasurement(Serializable):
    """
    A new Measurement has been added to the system.
    """
    measurement: Measurement
