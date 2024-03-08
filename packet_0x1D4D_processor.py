import re
from kpi_utils import simple_map_entry
class Packet_0x1D4D:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?Subscription ID = (?P<Subs_ID>[\d]+).*?Call ID = (?P<Call_ID>[\d]+).*?Call Status = (?P<Call_Status>[\d]+).*?CallTypeAtCallOrig = (?P<CallTypeAtCallOrig>.*?(?=\n)).*?CallTypeAtCallEnd = (?P<CallTypeAtCallEnd>.*?(?=\n)).*?Direction of Call = (?P<direction>.*?(?=\n)).*?CallSetup Time = (?P<callsetup_time>.*?(?=\n)).*?CallRingingRingback Time = (?P<callringback_time>.*?(?=\n)).*?CallRatatOrig = (?P<CallRatatOrig>.*?(?=\n)).*?CallRatatEnd = (?P<CallRatatEnd>.*?(?=\n)).*?Call End Indication Supressed = (?P<callend_indication_supressed>[\d]+).*?Redial at IMS layer Call type = (?P<redial_at_IMS_layer>.*?(?=\n)).*?IsCallAutoRejected = (?P<IsCallAutoRejected>[\d]+).*?AutoRejectReason = (?P<AutoRejectReason>.*?(?=\n)).*?LatestAudioCodec = (?P<LatestAudioCodec>.*?(?=\n)).*?HandoverStatsEnabled = (?P<HandoverStatsEnabled>[\d]+).*?EPSFBStatsEnabled = (?P<EPSFBStatsEnabled>[\d]+).*?SRVCCStatsEnabled = (?P<SRVCCStatsEnabled>[\d]+).*?CRSStatsEnabled = (?P<CRSStatsEnabled>[\d]+).*?EarlyMediaStatsEnabled = (?P<EarlyMediaStatsEnabled>[\d]+)"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None


