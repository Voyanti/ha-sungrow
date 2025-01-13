# Configuration
Before using, state all the modbus devices in `config.yaml`. Multiple servers and clients can be added

## Client
### Defini
`config.yaml` contains a template for Modbus RTT as defined for SunGrow inverters under options>connection_specs. Add a custom entry and specify it for each client in `config.yaml`
## Server
### Defining a new Server type
Inherit from server class in `server.py`. 
<!-- TODO -->
