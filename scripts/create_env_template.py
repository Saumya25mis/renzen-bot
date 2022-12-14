"""Create .env template"""

TEMPLATE = "DEV_DISCORD_TOKEN = ''"

with open(".enva", "x") as f:  # pylint:disable=unspecified-encoding
    f.write(TEMPLATE)
