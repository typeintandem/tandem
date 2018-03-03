from tandem.shared.io.proxies.base import ProxyBase
from tandem.shared.utils.relay import RelayUtils
from tandem.rendezvous.stores.session import SessionStore


class RendezvousRelayProxy(ProxyBase):
    def on_retrieve_io_data(self, params):
        args, kwargs = params
        raw_data, in_address = args

        if RelayUtils.is_relay(raw_data):
            payload, out_address = RelayUtils.deserialize(raw_data)
            new_data = RelayUtils.serialize(payload, in_address)

            # Check that the peers belong in the same session
            session_store = SessionStore.get_instance()
            in_session = session_store.get_session_from_address(in_address)
            out_session = session_store.get_session_from_address(out_address)
            if in_session != out_session:
                return (None, None)

            io_data = self._interface.generate_io_data(new_data, out_address)
            self._interface.write_io_data(io_data)

            return (None, None)
        else:
            return params
