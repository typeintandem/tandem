from tandem.shared.io.udp_gateway import UDPGateway
from tandem.shared.io.proxies.base import ProxyBase
from tandem.shared.utils.reliability import ReliabilityUtils
from tandem.shared.stores.reliability import ReliabilityStore
import logging


class ReliabilityProxy(ProxyBase):
    def __init__(self, time_scheduler):
        self._time_scheduler = time_scheduler

    def _handle_ack_timeout(self, ack_id, io_data):
        if ReliabilityUtils.should_resend_payload(ack_id):
            logging.info("Timeout on ack {}, resending".format(ack_id))
            self._interface._write_io_data([io_data])
            self._time_scheduler.run_after(
                ReliabilityUtils.ACK_TIMEOUT,
                self._handle_ack_timeout,
                ack_id,
                io_data
            )

    def pre_write_io_data(self, params):
        args, kwargs = params
        io_datas, = args
        should_ack = kwargs.get('reliability', False)

        if not should_ack:
            return params

        new_io_datas = []
        for io_data in io_datas:
            new_io_data = io_data
            new_raw_data, ack_id = ReliabilityUtils.serialize(
                io_data.get_data(),
            )
            new_io_data = UDPGateway.data_class(
                new_raw_data,
                io_data.get_address(),
            )

            ReliabilityStore.get_instance().add_payload(ack_id, new_io_data)
            self._time_scheduler.run_after(
                ReliabilityUtils.ACK_TIMEOUT,
                self._handle_ack_timeout,
                ack_id,
                new_io_data
            )

            new_io_datas.append(new_io_data)

        new_args = (new_io_datas,)
        return (new_args, kwargs)

    def on_retrieve_io_data(self, params):
        args, kwargs = params
        raw_data, address = args

        if ReliabilityUtils.is_ack(raw_data):
            ack_id = ReliabilityUtils.parse_ack(raw_data)
            ReliabilityStore.get_instance().remove_payload(ack_id)
            return (None, None)

        elif ReliabilityUtils.is_ackable(raw_data):
            new_raw_data, ack_id = ReliabilityUtils.deserialize(raw_data)
            ack_payload = ReliabilityUtils.generate_ack(ack_id)
            self._interface.write_io_data([
                self._interface.data_class(ack_payload, address),
            ])

            new_args = new_raw_data, address
            return (new_args, kwargs)

        else:
            return params
