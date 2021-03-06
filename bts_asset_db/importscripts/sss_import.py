import logging
import datetime
from io import BytesIO
from .sss_base import *
from bts_asset_db.models import *
from django.utils.timezone import make_aware
from django.db.models import Q


def sss_import(uploaded_files):
    logging.basicConfig(level=logging.INFO)

    for filename in uploaded_files:
        with open(filename, 'rb') as file:
            file_contents = BytesIO(file.read())
            try:
                read_sss(file_contents)
            except SSSSyntaxError as message:
                print('End File {Error:"%s"}' % message)
                continue

    update_machine_latest_record_times()


def update_machine_latest_record_times():
    for machine in TestingMachine.objects.all():
        try:
            timestamp = Record.objects.filter(machine_serial_no=machine).latest('timestamp', 'id').timestamp
        except ObjectDoesNotExist as e:
            timestamp = make_aware(datetime.datetime(1970, 1, 1, 0, 0))

        machine.last_imported_record_time = timestamp
        machine.save()


def read_sss(file_contents):
    records = get_records(file_contents, SSSRecordHeader())

    while True:
        try:
            payload = next(records)
        except StopIteration:
            # file parsing complete
            break

        parse_record(payload)


def get_records(file_contents, record_header):
    # Retrieve and validate records
    while True:
        header = file_contents.read(len(record_header))

        if not header:
            # we've hit the end of the file, stop now
            break

        record_header.unpack(header)

        if record_header.data['payload_length'] == 0:
            logging.warning('Zero length payload for a record')
            continue

        payload = file_contents.read(record_header.data['payload_length'])

        if not record_header.checksum(payload):
            logging.error('Checksum validation failed for a record')
            continue

        yield payload


def parse_record(payload):
    record = Record()
    tests = TESTS_VERSION_1.copy()
    version = 1

    test_type = None
    entries_to_create = []

    while payload and test_type != 0xff:
        test_type = payload[0]
        # Add in newer-style records if detected by presence of 0x11/0x12
        if version == 1 and test_type in (0x11, 0x12):
            version += 1
            tests.update(TESTS_VERSION_2)

        payload = payload[1:]

        # Unpack the current sub-field
        current_test = tests[test_type][1]()
        current_test.unpack(payload[:len(current_test)])
        entries_exported = export_record(record, current_test.data, test_type)
        if entries_exported is not None:
            entries_to_create += entries_exported

        # Seek past to start of next sub-field
        payload = payload[len(current_test):]

    if record.timestamp > record.machine_serial_no.last_imported_record_time:
        if not record.retest_freq_months:
            record.retest_freq_months = 12
        record.save()
        for entry in entries_to_create:
            entry.record = record
            entry.save()


def export_record(record, data, test_type):
    test = PatTest(test_type=test_type)
    entities_to_create = []

    if test_type in (0x01, 0x02, 0x11, 0x12):
        # Record a visual test result
        record.testcode_1 = data['testcode1']
        record.testcode_2 = data['testcode2']
        record.site = data['site']
        record.location = data['location']
        record.tester = Tester.objects.get(Q(machine_name=data['tester']) | Q(alt_machine_name=data['tester']))
        record.timestamp = make_aware(datetime.datetime(data['year'],
                                             data['month'],
                                             data['day'],
                                             data['hour'],
                                             data['minute']))

        record.item, _ = Item.objects.get_or_create(asset_id=data['id'])

    elif test_type == 0xe0:
        # User Data Input Order
        record.user_data_input_order = (data['mapping1'], data['mapping2'], data['mapping3'], data['mapping4'])

    elif test_type == 0xe1:
        # Retest Frequency
        record.retest_freq_months = data['frequency']

    elif test_type in range(0xf0, 0xfb):
        # These are individual tests, just lump parameters into one table
        test_params = [round(val, 4) if type(val) == float else val for val in data.values()]
        no_of_params = len(test_params)

        test.test_parameter_1 = test_params[0] if (no_of_params > 0) else None
        test.test_parameter_2 = test_params[1] if (no_of_params > 1) else None
        test.test_parameter_3 = test_params[2] if (no_of_params > 2) else None

        entities_to_create.append(test)

    elif test_type == 0xfb:
        # These are the user data fields. Assume we already have info about the data order.
        user_data = list(data.values())
        mappings = {0: "item_notes",
                    1: "item_description",
                    2: "item_group",
                    3: "item_make",
                    4: "item_model",
                    5: "item_serial_number"}

        # Deals with the fact multiple user_data entries may be of the same type.
        # If this happens, separate with /n.

        for mapping, fieldname in mappings.items():
            contents = [data
                        for ind, data in enumerate(user_data)
                        if record.user_data_input_order[ind] == mapping]
            if contents:
                combined_data = "\n".join(contents)
                setattr(record, fieldname, combined_data)

    elif test_type == 0xfe:
        # Tester serial number and firmware
        record.machine_serial_no_id = data['serialnumber']
        record.machine_firmware_version = '%d.%d.%d' % (data['firmware1'], data['firmware2'], data['firmware3'])

    else:
        # Unknown
        # logging.warning("Invalid or unknown type passed: %x" % test_type)
        pass

    return entities_to_create
