from tandem.shared.io.proxies.base import ProxyBase
from tandem.shared.utils.relay import RelayUtils
from tandem.rendezvous.stores.session import SessionStore


class RendezvousRelayProxy(ProxyBase):
    def on_retrieve_io_data(self, params):
        args, kwargs = params
        if args is None or args is (None, None):
            return params

        raw_data, in_address = args

        if RelayUtils.is_relay(raw_data):
            payload, out_address = RelayUtils.deserialize(raw_data)

            # Check that the peers belong in the same session
            session_store = SessionStore.get_instance()
            in_session = session_store.get_session_from_address(in_address)
            out_session = session_store.get_session_from_address(out_address)
            if in_session != out_session:
                return (None, None)

            new_data = RelayUtils.serialize(payload, in_address)

            # HACK: Write the data directly
            self._interface.write_io_data(
                [self._interface.data_class(new_data, out_address)],
                reliability=True,
            )

            return (None, None)
        else:
            return params
