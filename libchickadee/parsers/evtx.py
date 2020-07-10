"""Extract IP addresses from EVTX files."""

from libchickadee.parsers import ParserBase, run_parser_from_cli

import Evtx.Evtx


class EVTXParser(ParserBase):
    def __init__(self, ignore_bogon=True):
        super().__init__(ignore_bogon)
        self.ips = {}

    def parse_file(self, file_entry, is_stream=False):
        """Parse EVTX contents. Must be a path to an existing EVTX file.
        Cannot parse from STDIN.

        Args:
            file_entry (str): Path to EVTX file to load.
            is_stream (bool): Unused argument, required for implementation.
                Does not change functionality.
        """
        if is_stream:
            raise NotImplementedError("Providing EVTX files as an input stream of data is not yet supported.")

        # Open file
        with Evtx.Evtx.Evtx(file_entry) as event_log:
            # Iterate over events
            for record in event_log.records():
                # Send event data to self.check_ips()
                self.check_ips(record.xml())


if __name__ == "__main__":  # pragma: no cover
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="File or folder to parse")
    args = parser.parse_args()

    ev_parser = EVTXParser()
    run_parser_from_cli(args=args, parser_obj=ev_parser)

