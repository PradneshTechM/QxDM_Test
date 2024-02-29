import re
class Packet_0xB825:
    # def __int__(self):
    #     # print("New")



    def extract_info(lines, config, entry):
        # print("Lines", lines)
        # print("obj", dict)
        # return dict
        # pattern = r'.*?0xB801.*?--  (?P<msg_subtitle>.*?)\s*\nSubscription ID = (?P<subscription_id>\d+)\n.*?nr5g_smm_msg\s+(?P<nr5g_smm_msg>.*?)\n(?:.*?cause = (?P<_5gsm_cause>.*?)\n|.*?)'
        pattern = r'.*?0xB825.*?Subscription ID = (?P<Subscription_ID>\d+).*?Conn Config Info.*?State = (?P<State>\w+).*?LTE Serving Cell Info.*?Num Bands = (?P<num_bands>\d+).*?LTE Bands = (?P<lte_bands>.+).*?Num Contiguous CC Groups = (?P<num_cont_cc_groups>\d+).*?Num Active CC = (?P<num_active_cc>\d+).*?NR5G Serving Cell Info\n(?P<table>.+)?Radio Bearer Info.*?'
        # pattern = r'0xB825.*?Subscription ID = (?P<Subscription_ID>\d+).*?State = (?P<State>\w+).*?Num Bands = (?P<LTE_Bands_Num>\d+).*?\|Band\s+\|DL BW\s+\|UL BW\s+\|.*?\|(?P<Band>\d+)\s+\|(?P<DL_BW>\w+)\s+\|(?P<UL_BW>\w+)\s+\|.*?LTE Serving Cell Info.*?\|(?P<CC_Id>\d+)\|(?P<Cell_Id>\d+)\|(?P<DL_Arfcn>\d+)\|(?P<UL_Arfcn>\d+)\|(?P<Band_Type>\w+)\|.*?\|(?P<DL_Bandwidth>\S+)\|(?P<UL_Bandwidth>\S+)\|.*?\|(?P<DL_MIMO>\d+)\|(?P<UL_MIMO>\d+)\|'
        match = re.match(pattern, lines, re.DOTALL)

        # print(config)

        if match:
            entry.update(match.groupdict())
            # table_data = Packet_0xB825.extract_table_data(entry['table'])
            print(entry["table"])
            table_lines = entry["table"].strip().split('\n')
            # print(table_lines)
            for line in table_lines:
                print("dummy")
                print(line)
            return entry

        else:
            return None


