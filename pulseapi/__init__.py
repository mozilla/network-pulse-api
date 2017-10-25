import newrelic.agent
import os

if os.getenv('NEW_RELIC_LICENSE_KEY', None):
    newrelic.agent.initialize()
