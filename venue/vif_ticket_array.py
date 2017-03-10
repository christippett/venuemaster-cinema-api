from collections import defaultdict
from typing import Dict

from .vif_field_map import TICKET_ARRAY_FIELD_MAP
from .common import swap_schema_field_key


class VIFTicketArray(object):
    def __init__(self, record_code: str, ticket_array: Dict=None):
        self._tickets = []
        self.record_code = record_code
        if ticket_array is not None:
            parsed_ticket_array = self._parse_ticket_array(
                self._extract_ticket_fields_from_array(ticket_array)
            )
            self._load_tickets_from_array(parsed_ticket_array)

    def _extract_ticket_fields_from_array(self, d: Dict) -> Dict:
        return dict((k, v) for k, v in d.items() if int(k) > 100000)

    def _parse_ticket_array(self, d: Dict) -> Dict:
        parsed_ticket_array = defaultdict(dict)
        for key, value in d.items():
            ticket_counter = (int(key) - 100000) // 100
            field_number = (int(key) - 100000) % 100
            parsed_ticket_array[ticket_counter][field_number] = value
        return dict(parsed_ticket_array)

    def _load_tickets_from_array(self, d: Dict):
        for k, v in d.items():
            self._tickets.append(v)

    def tickets(self):
        tickets = []
        field_map = TICKET_ARRAY_FIELD_MAP.get(self.record_code)
        for ticket in self._tickets:
            english_ticket = {}
            for key, value in ticket.items():
                field_name, field_type = field_map.get(key, ('UNKNOWN_%s' % (key), str))
                english_ticket[field_name] = field_type(value)
            tickets.append(english_ticket)
        return tickets

    def add_ticket(self, **kwargs):
        field_map = TICKET_ARRAY_FIELD_MAP.get(self.record_code)
        reverse_field_map = swap_schema_field_key(field_map)
        ticket = {}
        for key, value in kwargs.items():
            integer_field, field_type = reverse_field_map.get(key, (None, None))
            if integer_field is not None:
                ticket[integer_field] = field_type(value)
            else:
                raise ValueError
        self._tickets.append(ticket)

    def count(self):
        return len(self._tickets)

    def _total_ticket_field(self, field):
        total = 0
        for ticket in self.tickets():
            total += float(ticket.get(field, 0))
        return total

    def total_ticket_prices(self):
        return self._total_ticket_field('ticket_price')

    def total_ticket_fees(self):
        return self._total_ticket_field('ticket_service_fee')

    def total(self):
        return self.total_ticket_prices() + self.total_ticket_fees()

    @property
    def data(self) -> Dict:
        array = list(enumerate(self._tickets, start=1))
        d = {}
        for i, ticket in array:
            ticket_key = 100000 + i * 100
            for key, value in ticket.items():
                d[ticket_key + key] = value
        return d
