enable_testing()
add_test(NAME UnitTests COMMAND python3 -m unittest discover -s /unit)
add_test(NAME IntegrationTests COMMAND python3 -m unittest discover -s /integration)
