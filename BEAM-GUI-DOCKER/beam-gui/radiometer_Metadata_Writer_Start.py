import os
from datetime import datetime
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self,
                 object_name="",
                 observation_type="",
                 rest_freq="",
                 bandwidth=0,
                 ra=0,
                 dec=0,
                 integration_time=0,
                 receiver="",
                 rf_gain=0,
                 if_gain=0,
                 bb_gain=0):
        gr.sync_block.__init__(
            self,
            name='Metadata Writer',
            in_sig=None,
            out_sig=None
        )

        # Store parameters
        self.object_name = object_name
        self.observation_type = observation_type
        self.rest_freq = rest_freq
        self.bandwidth = bandwidth
        self.ra = ra
        self.dec = dec
        self.integration_time = integration_time
        self.receiver = receiver
        self.rf_gain = rf_gain
        self.if_gain = if_gain
        self.bb_gain = bb_gain

        # Start timestamp and output filename
        self.start_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = f"observation_metadata_{self.start_timestamp}.txt"

        self.write_metadata()

    def write_metadata(self):
        with open(self.filename, 'w') as f:
            f.write(f"Observation_Start: {self.start_timestamp}\n")
            f.write(f"Object: {self.object_name}\n")
            f.write(f"Observation_Type: {self.observation_type}\n")
            f.write(f"Rest_Freq: {self.rest_freq}\n")
            f.write(f"Bandwidth: {self.bandwidth}\n")
            f.write(f"RA: {self.ra}\n")
            f.write(f"Dec: {self.dec}\n")
            f.write(f"Integration_Time: {self.integration_time}\n")
            f.write(f"Receiver: {self.receiver}\n")
            f.write(f"RF_Gain: {self.rf_gain}\n")
            f.write(f"IF_Gain: {self.if_gain}\n")
            f.write(f"BB_Gain: {self.bb_gain}\n")

        print(f"[INFO] Metadata written to: {self.filename}")

    def work(self, input_items, output_items):
        return 0
