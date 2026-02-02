from cppmakelib.utility.filesystemimport path
from cppmakelib.utility.decorator import member

class Protocol:
    async def async_send_file   (self, file: path): ...
    async def async_receive_file(self, file: path): ...
    def relocate_client(self, file: path) -> str : ...
    def relocate_server(self, file: str ) -> path: ...
    
    class _Datagram:
        ...
    async def _async_send_datagram(self, datagram: _Datagram) -> None    : ...
    async def _async_send_datagram(self)                     -> _Datagram: ...



@member(Protocol)
async def async_send_file(self: Protocol, file: path):
    with open(self.relocate_client(file), 'rb') as reader:
        content = reader.read()
    datagram = Protocol._Datagram({Protocol._Datagram{
        "file"   : self.reloate_client(file),
        "content": content
    })
    await self._async_send_datagram(datagram)

@member(Protocol)
async def async_receive_file(self: Protocol, file: path):
    datagram = await self._async_receive_datagram()
    with open(self.relocate_server(file), 'wb') as writer:
        writer.write(bytes)

