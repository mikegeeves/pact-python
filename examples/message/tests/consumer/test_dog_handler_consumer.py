"""pact test for a message consumer"""

import logging
import os

import pytest

from pact import MessageConsumer, Provider, Like, Term
from src.dog_handler import DogHandler, CustomError

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# For the purposes of this example, the broker is started up as a fixture defined
# in conftest.py. For normal usage this would be self-hosted or using Pactflow.
PACT_BROKER_URL = "http://localhost"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

# Where to output the JSON Pact files created by any tests
PACT_DIR = os.path.dirname(os.path.realpath(__file__))

CONSUMER_NAME = "MyPythonMessageConsumer"
PROVIDER_NAME = "MyPythonMessageProvider"


@pytest.fixture
def consumer() -> DogHandler:
    return DogHandler


@pytest.fixture(scope="session")
def pact(request):
    """Setup a Pact Consumer, which provides the Provider mock service. This
    will generate and optionally publish Pacts to the Pact Broker"""

    # When publishing a Pact to the Pact Broker, a version number of the Consumer
    # is required, to be able to construct the compatability matrix between the
    # Consumer versions and Provider versions
    version = request.config.getoption("--publish-pact")
    publish = True if version else False

    pact = MessageConsumer(CONSUMER_NAME, version=version).has_pact_with(
        Provider(PROVIDER_NAME),
        pact_dir=PACT_DIR,
        publish_to_broker=publish,
        broker_base_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME,
        broker_password=PACT_BROKER_PASSWORD,
    )

    yield pact


def test_valid_dog(pact: MessageConsumer, consumer):
    event = {
        "id": Like(1),
        "name": Like("rover"),
        "type": Term("^(bulldog|sheepdog)$", "bulldog"),
    }
    (
        pact.given("some state")
        .expects_to_receive("a request for a dog")
        .with_content(event)
        .with_metadata({"Content-Type": "application/json"})
    )

    with pact:
        # All we need to do is send the event to the consumer
        consumer(event)


def test_invalid_dog(pact: MessageConsumer, consumer):
    event = {"name": "fido"}
    (
        pact.given("some state")
        .expects_to_receive("a request for a dog")
        .with_content(event)
        .with_metadata({"Content-Type": "application/json"})
    )

    with pytest.raises(CustomError):
        with pact:
            # All we need to do is send the event to the consumer
            consumer(event)
